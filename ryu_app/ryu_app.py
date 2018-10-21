from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller.dpset import EventDP
from ryu.lib.packet import packet
from ryu.utils import hex_array

import binascii

switch_db = {

}

class FlowInstaller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):

        super(FlowInstaller, self).__init__(*args, **kwargs)
        print(" active ")

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

        print("Data: {}".format(packet.Packet(ev.msg.data)))
        print("Table: {}".format(ev.msg.table_id))
        print("Reason: {}".format(reason))


    @set_ev_cls(ofp_event.EventOFPMsgBase, MAIN_DISPATCHER)
    def ofp_base(self, ev):
        print("--> {}".format(ev))


    @set_ev_cls(EventDP, MAIN_DISPATCHER)
    def event_dp(self, ev):
        print("Switch Address: {}    Enter: {}".format(ev.dp.address, ev.enter))

        if ev.enter:
            switch_db[ev.dp.address] = {
                "dp": ev.dp,
                "ports": ev.ports
            }

            for port in ev.ports:
                print("Added flow to: {}".format(port))
                FlowFactory.add_packet_in_flow(ev.dp, port)
        else:
            if switch_db.get(ev.dp.address):
                del switch_db[ev.dp.address]


class FlowFactory(object):

    @staticmethod
    def add_packet_in_flow(datapath, port):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(in_port=port[0])

        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER), parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, instructions=inst)

        datapath.send_msg(mod)

