# 1 HEX = 4 BITS
import logging
from packet_processor_layer3 import IPv4, IPv6, Geneve, Arp

class Ethernet():
    # Ethernet Header:
    # DST MAC 6 bytes, SRC MAC 6 bytes, TYPE 2 bytes, PAYLOAD 46-1500 bytes
    @staticmethod
    def build(hex_array):
        src_mac = hex_array[0:12]
        dst_mac = hex_array[12:24]
        ether_type = hex_array[24:28]
        payload = hex_array[28:]

        return Ethernet(dst_mac, src_mac, ether_type, payload)

    @staticmethod
    def format_mac_address(mac):
        return f"{mac[0:2]}:{mac[2:4]}:{mac[4:6]}:{mac[6:8]}:{mac[8:10]}:{mac[10:12]}"

    @staticmethod
    def get_next_processor(packet):

        if packet.ether_type == "0800":
            return IPv4
        elif packet.ether_type == "0806":
            return Arp
        elif packet.ether_type == "86dd":
            return IPv6
        elif packet.ether_type == "0006":
            return Geneve
        else:
            raise Exception(f"Unknown Ether Type: {packet.ether_type}")

    def __init__(self, dst_mac, src_mac, ether_type, payload):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.ether_type = ether_type
        self.payload = payload

    def data(self):

        return {
            "structure": "Ethernet",
            "src_mac": Ethernet.format_mac_address(self.src_mac),
            "dst_mac": Ethernet.format_mac_address(self.dst_mac),
            "ether_type": self.ether_type,
            "payload": self.payload
        }

    def __str__(self):

        return f"Source: {Ethernet.format_mac_address(self.src_mac)}\tDest.: {Ethernet.format_mac_address(self.dst_mac)}\tEther Type: {self.ether_type}\tData Length: {len(self.payload)}\n"

class PacketProcessor():

    l2_processors = [Ethernet]

    @staticmethod
    def build(hex_array):
        results = {}
        for l2_proc in PacketProcessor.l2_processors:
            layers = []
            try:
                result_l2 = l2_proc.build(hex_array)

                if result_l2:
                    try:
                        results["LAYER2"] = {
                            l2_proc.__name__: result_l2.data()
                        }
                        layers.append(result_l2.data().get("structure"))
                        l3_proc = l2_proc.get_next_processor(result_l2)

                        if not l3_proc:
                            break

                        result_l3 = l3_proc.build(result_l2.payload)

                        if result_l3:

                            results["LAYER3"] = {
                                l3_proc.__name__: result_l3.data()
                            }
                            layers.append(result_l3.data().get("structure"))
                            try:
                                l4_proc = l3_proc.get_next_processor(result_l3)

                                if not l4_proc:
                                    break

                                result_l4 = l4_proc.build(result_l3.payload)

                                if result_l4:

                                    results["LAYER4"] = {
                                        l4_proc.__name__: result_l4.data()
                                    }
                                    layers.append(result_l4.data().get("structure"))
                            except:
                                logging.exception("Error process Layer 4")

                    except:
                        logging.exception("Error process Layer 3")

            except:
                logging.exception("Error process Layer 2")

        return results, layers

