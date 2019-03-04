
from pymongo import MongoClient
import socket
import struct
import binascii
from collections import Counter
from matplotlib import pyplot as plt

MONGO_HOST = "192.168.0.19"
MONGO_PORT = 27017

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet

count = 0
counter = Counter()
lst = []
for doc in collection.find():
    data = binascii.hexlify(doc["packet"]).decode('latin-1')
    src_mac = data[0:12]
    dst_mac = data[12:24]
    ether_type = data[24:28]
    payload = data[28:]
    print(f"Src: {src_mac}\nDst: {dst_mac}\nEther Type: {ether_type}\nData: {len(payload)}")
    print(payload[0], payload[1], payload[2:4], payload[4:8], payload[8: 12], payload[16:18],payload[18:20])
    src_ip = payload[24:32]
    src_ip = [int(src_ip[0:2],16), int(src_ip[2:4],16), int(src_ip[4:6],16), int(src_ip[6:8],16)]
    print(src_ip)

    dst_ip = payload[32:40]
    dst_ip = [int(dst_ip[0:2],16), int(dst_ip[2:4],16), int(dst_ip[4:6],16), int(dst_ip[6:8],16)]
    print(dst_ip)
    #lst.append(len(payload))
    #print(data[0:12].decode('latin-1'), data[12:24].decode('latin-1'), data[24:28].decode('latin-1'))
    # mac = int(data[1:6], base=2)
    # print(mac)
    #lst.append((len(bin(int(binascii.hexlify(doc["packet"]), base=16)))-2)/8)
    # print(bin(int(binascii.hexlify(doc["packet"]), base=16)))
    # print(bin(int(binascii.hexlify(doc["packet"]), base=16))[2])

    count+=1
    print("\n\nNexT:")

print(count)
print(Counter(lst))

plt.hist(lst,bins=20)
plt.show()