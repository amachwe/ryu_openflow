from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller.dpset import EventDP
from ryu.lib.packet import packet, ethernet, ipv4, arp, dhcp, icmp, vlan, lldp, tcp, udp

import pprint

switch_db = {

}

INTERNET_PORT = {
    63466001429: 1
}
SHADOW_PORT = {
    63466001429: 2
}
INTERNAL_PORT = {
    63466001429: 3
}


#Zodiac FX
# INTERNET_PORT = {
#     123917682138647: 1
# }
# SHADOW_PORT = {
#     123917682138647: 2
# }
# INTERNAL_PORT = {
#     123917682138647: 3
# }


fh = open('protocol.json', 'w')
protocols = (ethernet.ethernet, ipv4.ipv4, icmp.icmp, dhcp.dhcp, arp.arp, vlan.vlan, lldp.lldp, tcp.tcp, udp.udp)
class FlowInstaller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):

        super(FlowInstaller, self).__init__(*args, **kwargs)
        print(" \nactive ")

    def packet_processor(self, packet):
        packet_data = {}
        for protocol_handler in protocols:
            packet_data[protocol_handler] = packet.get_protocol(protocol_handler)

        pprint.pprint(packet_data, fh)
        fh.write(",\n")
        return packet_data


    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_rem(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        if msg.reason == ofp.OFPRR_IDLE_TIMEOUT:
            reason = 'IDLE TIMEOUT'
        elif msg.reason == ofp.OFPRR_HARD_TIMEOUT:
            reason = 'HARD TIMEOUT'
        elif msg.reason == ofp.OFPRR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPRR_GROUP_DELETE:
            reason = 'GROUP DELETE'
        else:
            reason = 'unknown'



        print(f"Flow removed {reason} {msg.match['in_port']}")



    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):

        ofproto = ev.msg.datapath.ofproto

        reason = ev.msg.reason

        if reason == ofproto.OFPR_NO_MATCH:
            reason = "No match"
        elif reason == ofproto.OFPR_ACTION:
            reason = "Action"
        elif reason == ofproto.OFPR_INVALID_TTL:
            reason = 'Invalid TTL'
        else:
            reason = 'Unknown'

        pkt = packet.Packet(ev.msg.data)

        packet_data = self.packet_processor(pkt)


    @set_ev_cls(ofp_event.EventOFPMsgBase, MAIN_DISPATCHER)
    def ofp_base(self, ev):
        print("--> {}".format(ev))

    @set_ev_cls(EventDP, MAIN_DISPATCHER)
    def event_dp(self, ev):
        print("Switch Address: {}    Enter: {}".format(ev.dp.address, ev.enter))

        if ev.enter and not switch_db.get(ev.dp.address):
            print("DP Id: ",ev.dp.id)
            print("Ports: ","\n".join([repr(p) for p in ev.ports]))
            switch_db[ev.dp.address] = {
                "dp": ev.dp,
                "ports": ev.ports
            }

            sw_internet_port = None
            sw_shadow_port = None
            sw_internal_port = None
            for port in ev.ports:
                if port.port_no == INTERNET_PORT[ev.dp.id]:
                    sw_internet_port = port
                elif port.port_no == SHADOW_PORT[ev.dp.id]:
                    sw_shadow_port = port
                elif port.port_no == INTERNAL_PORT[ev.dp.id]:
                    sw_internal_port = port

            if not sw_internet_port or not sw_internal_port or not sw_shadow_port:
                return

            FlowFactory.add_bridge_flow(ev.dp, sw_internal_port.port_no, [sw_internet_port.port_no, sw_shadow_port.port_no], pin=False)
            FlowFactory.add_bridge_flow(ev.dp, sw_internet_port.port_no, [sw_internal_port.port_no, sw_shadow_port.port_no], pin=False)

        else:
            del switch_db[ev.dp.address]


class FlowFactory(object):


    @staticmethod
    def add_bridge_flow(datapath, port_in, port_outs, pin=True):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print(port_in, port_outs)

        match = parser.OFPMatch(in_port=port_in)
        actions = [parser.OFPActionOutput(port_out) for port_out in port_outs]

        if pin:
            actions.append(parser.OFPActionOutput(ofproto.OFPP_CONTROLLER))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=100,
            flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)

        datapath.send_msg(mod)

    @staticmethod
    def add_rev_bridge_flow(datapath, port_in, port_outs, pin=True):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(in_port=port_in.port_no)
        actions = list([parser.OFPActionOutput(port_out.port_no) for port_out in port_outs])

        if pin:
            actions.append(parser.OFPActionOutput(ofproto.OFPP_CONTROLLER))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=100,
            flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)

        datapath.send_msg(mod)


