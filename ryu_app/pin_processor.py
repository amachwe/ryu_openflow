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
    123917682138647: 1
}


fh = open('protocol.json', 'w')
protocols = (ethernet.ethernet, ipv4.ipv4, icmp.icmp, dhcp.dhcp, arp.arp, vlan.vlan, lldp.lldp, tcp.tcp, udp.udp)
class FlowInstaller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):

        super(FlowInstaller, self).__init__(*args, **kwargs)
        print(" active ")

    def packet_processor(self, packet):
        packet_data = {}
        for protocol_handler in protocols:
            packet_data[protocol_handler] = packet.get_protocol(protocol_handler)
            if packet.get_protocol(protocol_handler):
                print(protocol_handler)

        pprint.pprint(packet_data, fh)
        fh.write(",\n")
        return packet_data


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