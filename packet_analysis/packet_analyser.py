
from pymongo import MongoClient
import socket
import struct
import binascii
import multiprocessing
from collections import Counter
from matplotlib import pyplot as plt

from packet_processor_layer2 import Ethernet, PacketProcessor


MONGO_HOST = "192.168.0.19"
MONGO_PORT = 27017

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet

count = 0
counter = Counter()
lst = []

def update_doc(doc):
    global count
    if doc.get("layers"):

        return

    count+=1
    data = binascii.hexlify(doc["packet"]).decode('latin-1')
    id = doc["_id"]
    try:
        results, layers = PacketProcessor.build(data)
        if results:
            collection.update_one(
                {
                    "_id": id
                },
                {
                    "$set": {
                        "layers": layers,
                        "extracted": results
                    }
                },
                True
            )


    except Exception as e:
        print(e)

if __name__ == '__main__':
    print("Starting... ")
    import time
    start_time = time.time()


    with multiprocessing.Pool(4) as pool:

        list(pool.imap(update_doc, collection.find()))

    print("------ waiting -------S")


    print(time.time()-start_time)
    print(count)
    print(Counter(lst))

    plt.hist(lst,bins=200)
    plt.show()