from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller.dpset import EventDP
from ryu.lib.packet import packet, ethernet, ipv4, arp, dhcp, icmp, vlan

import pprint

switch_db = {

}

host_learning = {

}

inv_host_learning = {

}

flow_inventory = {

}

fh = open('protocol.json', 'w')
protocols = (ethernet.ethernet, ipv4.ipv4, icmp.icmp, dhcp.dhcp, arp.arp, vlan.vlan)
class FlowInstaller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):

        super(FlowInstaller, self).__init__(*args, **kwargs)
        print(" active ")

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

        flow_key = (dp, msg.match['in_port'], msg.match['eth_src'])
        if flow_inventory.get(flow_key):
            del flow_inventory[flow_key]
        else:
            print(f"Error: flow not found: {flow_key}")

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

        in_port = ev.msg.match['in_port']

        src_mac = packet_data[ethernet.ethernet].src
        dst_mac = packet_data[ethernet.ethernet].dst
        dp = ev.msg.datapath


        port_key = (dp, in_port)
        host_key = (dp, src_mac)
        dst_key = (dp, dst_mac)

        if host_learning.get(port_key):
            temp_src_mac = host_learning.get(port_key)
            del host_learning[port_key]
            del inv_host_learning[temp_src_mac]

        host_learning[port_key] = host_key
        inv_host_learning[host_key] = port_key

        if dst_mac and inv_host_learning.get(dst_key):
            out_port = inv_host_learning[dst_key][1]
            flow_key = (dp, in_port, src_mac)

            if not flow_inventory.get(flow_key):
                print(f"Flow installing: {in_port} -> {out_port}")
                FlowFactory.add_passthrough_flow(dp, in_port, host_key[1], out_port)
                flow_inventory[flow_key] = True


    @set_ev_cls(ofp_event.EventOFPMsgBase, MAIN_DISPATCHER)
    def ofp_base(self, ev):
        print("--> {}".format(ev))


    @set_ev_cls(EventDP, MAIN_DISPATCHER)
    def event_dp(self, ev):
        print("Switch Address: {}    Enter: {}     DP: {}".format(ev.dp.address, ev.enter, ev.dp))

        if ev.enter:
            switch_db[ev.dp.address] = {
                "dp": ev.dp,
                "ports": ev.ports
            }

            for port in ev.ports:
                print("Added flow to: {}:{}".format(ev.dp.id, port))
                FlowFactory.add_packet_in_flow(ev.dp, port)
        else:
            if switch_db.get(ev.dp.address):
                del switch_db[ev.dp.address]


class FlowFactory(object):

    @staticmethod
    def add_packet_in_flow(datapath, port, pin=True):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(in_port=port[0])
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

        if pin:
            actions.append(parser.OFPActionOutput(ofproto.OFPP_CONTROLLER))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=0,
            flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)

        datapath.send_msg(mod)

    @staticmethod
    def add_passthrough_flow(datapath, port_in, src_mac, port_out, pin=True):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(in_port=port_in, eth_src=src_mac)
        actions = [parser.OFPActionOutput(port_out)]

        if pin:
            actions.append(parser.OFPActionOutput(ofproto.OFPP_CONTROLLER))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=60, hard_timeout=300,
            priority=100,
            flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)

        datapath.send_msg(mod)


