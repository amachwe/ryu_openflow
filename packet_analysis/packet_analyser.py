
from pymongo import MongoClient
import socket
import struct
import binascii
from collections import Counter
from matplotlib import pyplot as plt

from packet_processor import Ethernet, IPv4

MONGO_HOST = "192.168.0.19"
MONGO_PORT = 27017

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet

count = 0
counter = Counter()
lst = []

import time
start_time = time.time()
for doc in collection.find():
    data = binascii.hexlify(doc["packet"]).decode('latin-1')

    l2 = Ethernet.build(data)


    l3 = Ethernet.get_next_processor(l2)


    count+=1

print(time.time()-start_time)
print(count)
print(Counter(lst))

plt.hist(lst,bins=200)
plt.show()