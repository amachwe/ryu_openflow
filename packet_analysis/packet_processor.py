# 1 HEX = 4 BITS
import logging

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

class Arp():

    @staticmethod
    def build(hex_array):
        arp = Arp()
        arp.hardware_type = hex_array[0:4]
        arp.protocol_type = hex_array[4:8]
        arp.hardware_addr_len = hex_array[8:10]
        arp.protocol_addr_len = hex_array[10:12]
        arp.operation = hex_array[12:16]

        if int(arp.hardware_addr_len, 16) == 6:
            arp.sender_hw_add = hex_array[16:28]
            arp.target_hw_add = hex_array[36:48]

        if int(arp.protocol_addr_len, 16) == 4:
            arp.sender_proto_add = hex_to_ip(hex_array[28:36])
            arp.target_proto_add = hex_to_ip(hex_array[48:56])

        return arp

    def __init__(self):
        self.hardware_type = 0
        self.protocol_type = 0
        self.hardware_addr_len = 0
        self.protocol_addr_len = 0
        self.operation = 0
        self.sender_hw_add = ""
        self.sender_proto_add = []
        self.target_hw_add = ""
        self.target_proto_add = []

    def data(self):
        return {
            "structure": "ARP",
            "hardware_type": self.hardware_type,
            "protocol_type": self.protocol_type,
            "hardware_address_length": self.hardware_addr_len,
            "protocol_address_length": self.protocol_addr_len,
            "operation": self.operation,
            "sender_hardware_address": self.sender_hw_add,
            "sender_protocol_address": self.sender_proto_add,
            "target_hardware_address": self.target_hw_add,
            "target_protocol_address": self.target_proto_add
        }

    def __str__(self):

        return f"Hardware Type: {self.hardware_type}\tProtocol Type: {self.protocol_type}\n" \
            f"Hardware Address Length: {self.hardware_addr_len}\tProtocol Address Length: {self.protocol_addr_len}\n" \
            f"Operation: {self.operation}\n" \
            f"Hardware Address: {self.sender_hw_add} to {self.target_hw_add}\n" \
            f"Protocol Address: {self.sender_proto_add} to {self.target_proto_add}\n"

class IPv6():

    @staticmethod
    def build(hex_array):
        ipv6 = IPv6()

        ipv6.version = hex_array[0]
        ipv6.traffic_class = bin(int(hex_array[1:3], 16))[2:].zfill(8)
        ipv6.diff_service = ipv6.traffic_class[0:6]
        ipv6.ecn = ipv6.traffic_class[6:]
        ipv6.flow_label = int(hex_array[3:8], 16)
        ipv6.payload_length = int(hex_array[8:12], 16)
        ipv6.next_header = int(hex_array[12:14], 16)
        ipv6.hop_limit = int(hex_array[14:16], 16)
        ipv6.source_address = hex_array[16:48]
        ipv6.destination_address = hex_array[48:80]
        ipv6.payload = hex_array[80:]

        return ipv6

    def __init__(self):
        self.version = 0
        self.traffic_class = 0
        self.ecn = 0
        self.diff_service = 0
        self.flow_label = 0
        self.payload_length = 0
        self.next_header = 0
        self.hop_limit = 0
        self.source_address = 0
        self.destination_address = 0
        self.payload = ""

    def data(self):
        return {
            "structure": "IPv6",
            "version": self.version,
            "traffic_class": self.traffic_class,
            "diff_service": self.diff_service,
            "ecn": self.ecn,
            "flow_label": self.flow_label,
            "payload_length": self.payload_length,
            "next_header": self.next_header,
            "hop_limit": self.hop_limit,
            "source_address": self.source_address,
            "destination_address": self.destination_address
        }

    def __str__(self):

        return f"Version: {self.version}\tTraffic Class: {self.traffic_class}\tDiff Service: {self.diff_service}\tECN: {self.ecn}\n" \
            f"Flow Label: {self.flow_label}\n" \
            f"Payload Length: {self.payload_length}\tNext Header: {self.next_header}\tHop Limit: {self.hop_limit}\n" \
            f"Source Address: {self.source_address}\n" \
            f"Dest. Address: {self.destination_address}\n"


class Geneve():

    @staticmethod
    def build(hex_array):
        geneve = Geneve()
        bin_data = bin(int(hex_array[0:96],16))[2:].zfill(96)

        geneve.v = int(bin_data[0:2],2)
        geneve.option_length = bin_data[2:8]
        geneve.o = bin_data[8]
        geneve.c = bin_data[9]
        geneve.reserved_1 = bin_data[10:16]
        geneve.protocol_type = hex(int(bin_data[16:32],2))
        geneve.virt_net_id = bin_data[32:56]
        geneve.reserved_2 = bin_data[56:64]
        geneve.variable_len_opts = bin_data[64:96]
        geneve.payload = bin_data[96:]

        return geneve

    def __init__(self):
        self.v = 0
        self.option_length = 0
        self.o = 0
        self.c = 0
        self.reserved_1 = 0
        self.reserved_2 = 0
        self.protocol_type = 0
        self.virt_net_id = 0
        self.variable_len_opts = 0
        self.payload = 0


    def data(self):
        return {
            "structure": "Geneve",
            "v": self.v,
            "option_length": self.option_length,
            "o": self.o,
            "c": self.c,
            "reserved_1": self.reserved_1,
            "reserved_2": self.reserved_2,
            "protocol_type": self.protocol_type,
            "virtual_network_id": self.virt_net_id,
            "variable_length_options": self.variable_len_opts
        }

    def __str__(self):
        return f"V: {self.v}\tOption Length: {self.option_length}\tO: {self.o}\tC: {self.c}\n" \
            f"Reserved 1: {self.reserved_1}\tReserved 2: {self.reserved_2}\n" \
            f"Protocol Type: {self.protocol_type}\n" \
            f"Virtual Network Id: {self.virt_net_id}\n" \
            f"Variable Length Options: {self.variable_len_opts}\n"

class IPv4():
    # IPV4: (32 bit each)
    # - Version, IHL, DSCP, ECN, Total Length
    # - Identification, Flags, Fragment Offset
    # - TTL, Protocol, Header Checksum
    # - Src IP
    # - Dst IP
    # - Options
    # - Data
    @staticmethod
    def build(hex_array):

        ipv4 = IPv4()
        ipv4.version = hex_array[0]
        ipv4.ihl = hex_array[1]
        dscp_ecn = bin(int(hex_array[2:4], 16))[2:].zfill(8)
        ipv4.dscp = int(dscp_ecn[0:6],2)
        ipv4.ecn = int(dscp_ecn[6:8], 2)
        ipv4.total_length = int(hex_array[4:8], 16)
        ipv4.identification = hex_array[8:12]


        flags_frag_off = bin(int(hex_array[12:16], 16))[2:].zfill(16)
        ipv4.flags = flags_frag_off[0:3]
        ipv4.fragment_offset = int(flags_frag_off[3:], 2)

        ipv4.ttl = int(hex_array[16:18], 16)
        ipv4.protocol = int(hex_array[18:20], 16)
        ipv4.header_checksum = hex_array[20:24]

        src_ip = hex_to_ip(hex_array[24:32])

        ipv4.src_ip = src_ip

        dst_ip = hex_to_ip(hex_array[32:40])

        ipv4.dst_ip = dst_ip

        ipv4.payload = hex_array[40:]

        return ipv4


    def __init__(self):
        self.src_ip = []
        self.dst_ip = []
        self.options = []
        self.payload = ""

        self.ttl = 0
        self.protocol = None
        self.header_checksum = None
        self.identification = None
        self.flags = None
        self.fragment_offset = None
        self.version = None
        self.ihl = None
        self.dscp = None
        self.ecn = None
        self.total_length = 0

    def data(self):
        return {
            "structure": "IPv4",
            "version": self.version,
            "ihl": self.ihl,
            "dscp": self.dscp,
            "ecn": self.ecn,
            "total-length": self.total_length,
            "identification": self.identification,
            "flags": self.flags,
            "fragment-offset": self.fragment_offset,
            "ttl": self.ttl,
            "protocol": self.protocol,
            "header-checksum": self.header_checksum,
            "source-ip": self.src_ip,
            "destination-ip": self.dst_ip
        }

    def __str__(self):

        return f"IPv4 Version: {self.version}, IHL: {self.ihl}, DSCP: {self.dscp}, ECN: {self.ecn}" \
            f" Total Length: {self.total_length}" \
            f"\nIdentification: {self.identification}, Flags: {self.flags}, Fragment Offset: {self.fragment_offset}"\
            f"\nTTL: {self.ttl}, Protocol: {self.protocol}, Header Checksum: {self.header_checksum}" \
            f"\nSrc. IP: {self.src_ip}\nDst. IP: {self.dst_ip}\n"


class PacketProcessor():

    l2_processors = [Ethernet]

    @staticmethod
    def build(hex_array):
        results = {}
        for l2_proc in PacketProcessor.l2_processors:
            try:
                result_l2 = l2_proc.build(hex_array)

                if result_l2:
                    try:
                        results["LAYER2"] = {
                            l2_proc.__name__: result_l2
                        }
                        l3_proc = l2_proc.get_next_processor(result_l2)

                        result_l3 = l3_proc.build(result_l2.payload)

                        if result_l3:

                            results["LAYER3"] = {
                                l3_proc.__name__: result_l3
                            }

                    except:
                        logging.exception("Error process Layer 3")

            except:
                logging.exception("Error process Layer 2")

        return results

def hex_to_ip(hex_array):
    return [int(hex_array[0:2], 16), int(hex_array[2:4], 16), int(hex_array[4:6], 16), int(hex_array[6:8], 16)]