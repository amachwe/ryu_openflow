# 1 HEX = 4 BITS
import json

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

    def __init__(self, dst_mac, src_mac, ether_type, payload):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.ether_type = ether_type
        self.payload = payload

    def data(self):

        return {
            "src_mac": Ethernet.format_mac_address(self.src_mac),
            "dst_mac": Ethernet.format_mac_address(self.dst_mac),
            "ether_type": self.ether_type,
            "payload": self.payload
        }

    def __str__(self):

        return f"Source: {Ethernet.format_mac_address(self.src_mac)}\tDest.: {Ethernet.format_mac_address(self.dst_mac)}\tEther Type: {self.ether_type}\tData Length: {len(self.payload)}"

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

        src_ip = hex_array[24:32]
        src_ip = [int(src_ip[0:2], 16), int(src_ip[2:4], 16), int(src_ip[4:6], 16), int(src_ip[6:8], 16)]

        ipv4.src_ip = src_ip

        dst_ip = hex_array[32:40]
        dst_ip = [int(dst_ip[0:2], 16), int(dst_ip[2:4], 16), int(dst_ip[4:6], 16), int(dst_ip[6:8], 16)]

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
            "Version": self.version,
            "IHL": self.ihl,
            "DSCP": self.dscp,
            "ECN": self.ecn,
            "Total-Length": self.total_length,
            "Identification": self.identification,
            "Flags": self.flags,
            "Fragment-Offset": self.fragment_offset,
            "TTL": self.ttl,
            "Protocol": self.protocol,
            "Header-Checksum": self.header_checksum,
            "Source-IP": self.src_ip,
            "Destination-IP": self.dst_ip
        }

    def __str__(self):

        return f"IPv4 Version: {self.version}, IHL: {self.ihl}, DSCP: {self.dscp}, ECN: {self.ecn}" \
            f" Total Length: {self.total_length}" \
            f"\nIdentification: {self.identification}, Flags: {self.flags}, Fragment Offset: {self.fragment_offset}"\
            f"\nTTL: {self.ttl}, Protocol: {self.protocol}, Header Checksum: {self.header_checksum}" \
            f"\nSrc. IP: {self.src_ip}\nDst. IP: {self.dst_ip}"