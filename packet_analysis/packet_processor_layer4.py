# 1 HEX = 4 BITS

class IGMP():

    @staticmethod
    def build(hex_array):
        igmp = IGMP()

        return igmp

    def __init__(self):
        pass

    @staticmethod
    def get_next_processor(packet):
        return None

    def data(self):

        return {
            "structure": "IGMP"
        }

class ICMP():

    @staticmethod
    def build(hex_array):
        icmp = ICMP()

        return icmp

    def __init__(self):
        pass

    @staticmethod
    def get_next_processor(packet):
        return None

    def data(self):

        return {
            "structure": "ICMP"
        }

class TCP():

    @staticmethod
    def build(hex_array):
        tcp = TCP()

        tcp.src_port = int(hex_array[0:4], 16)
        tcp.dst_port = int(hex_array[4:8], 16)
        tcp.seq_num = int(hex_array[8:16], 16)
        tcp.ack_num = int(hex_array[16:24], 16)
        tcp.data_offset = int(hex_array[24], 16)

        flags_tcp = bin(int(hex_array[25:28], 16))[2:].zfill(12)
        tcp.reserved = flags_tcp[0:3]
        tcp.flags_NS = flags_tcp[3]
        tcp.flags_CWR = flags_tcp[4]
        tcp.flags_ECE = flags_tcp[5]
        tcp.flags_URG = flags_tcp[6]
        tcp.flags_ACK = flags_tcp[7]
        tcp.flags_PSH = flags_tcp[8]
        tcp.flags_RST = flags_tcp[9]
        tcp.flags_SYN = flags_tcp[10]
        tcp.flags_FIN = flags_tcp[11]

        tcp.window_size = int(hex_array[28:32], 16)
        tcp.checksum = hex_array[32:36]
        tcp.urgent = int(hex_array[36:40], 16)

        return tcp

    def __init__(self):
        self.payload = ""
        self.src_port = 0
        self.dst_port = 0
        self.seq_num = 0
        self.ack_num = 0
        self.window_size = 0
        self.reserved = 0
        self.data_offset = 0

        self.flags_NS = False
        self.flags_CWR = False
        self.flags_ECE = False
        self.flags_URG = False
        self.flags_ACK = False
        self.flags_PSH = False
        self.flags_RST = False
        self.flags_SYN = False
        self.flags_FIN = False
        self.checksum = 0
        self.urgent = 0


    @staticmethod
    def get_next_processor(packet):

        return None

    def data(self):
        return {
            "structure": "TCP",
            "source-port": self.src_port,
            "destination-port": self.dst_port,
            "sequence-number": self.seq_num,
            "ack-number": self.ack_num,
            "window-size": self.window_size,
            "reserved": self.reserved,
            "data-offset": self.data_offset,
            "NS": self.flags_NS,
            "CWR": self.flags_CWR,
            "ECE": self.flags_ECE,
            "URG": self.flags_URG,
            "ACK": self.flags_ACK,
            "PSH": self.flags_PSH,
            "RST": self.flags_RST,
            "SYN": self.flags_SYN,
            "FIN": self.flags_FIN,
            "checksum": self.checksum,
            "urgent": self.urgent

        }

    def __str__(self):

        return "\n".join([f"{k}: {v}" for k,v in self.data().items()])



class UDP():

    @staticmethod
    def build(hex_array):
        udp = UDP()

        udp.src_port = int(hex_array[0:4], 16)
        udp.dst_port = int(hex_array[4:8], 16)
        udp.length = int(hex_array[8:12], 16)
        udp.checksum = hex_array[12:16]

        return udp

    def __init__(self):
        self.payload = ""
        self.src_port = 0
        self.dst_port = 0
        self.length = 0
        self.checksum = 0

    @staticmethod
    def get_next_processor(packet):

        return None

    def data(self):
        return {
            "structure": "UDP",
            "source-port": self.src_port,
            "destination-port": self.dst_port,
            "length": self.length,
            "checksum": self.checksum
        }

    def __str__(self):

        return "\n".join([f"{k}: {v}" for k,v in self.data().items()])




def hex_to_ip(hex_array):
    return [int(hex_array[0:2], 16), int(hex_array[2:4], 16), int(hex_array[4:6], 16), int(hex_array[6:8], 16)]