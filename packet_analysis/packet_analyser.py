
from pymongo import MongoClient
import socket
import struct
import binascii
import multiprocessing
from collections import Counter
from matplotlib import pyplot as plt

from packet_processor_layer2 import Ethernet, PacketProcessor


MONGO_HOST = "localhost" #"192.168.0.19"
MONGO_PORT = 27017

HEX_MTU = 1522*4

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet



reset = True
print(f"Reset: {reset}")

def update_doc(doc):

    if not reset and doc.get("layers"):
        return


    data = binascii.hexlify(doc["packet"]).decode('latin-1')
    id = doc["_id"]
    try:
        results, layers = PacketProcessor.build(data)
        # _x = []
        _y = '_'.join([x for x in layers])
        len_x = len(data)

        # for i in range(0, len_x):
        #     _x.append(int(data[i], 16) / 15)
        #
        # for i in range(len_x * 4, HEX_MTU):
        #     _x.append(-1.0)
        if results:
            collection.update_one(
                {
                    "_id": id
                },
                {
                    "$set": {
                        "layers": layers,
                        "extracted": results,
  #                      "X": _x,
                        "Y": _y,
                        "Length": len_x
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


    with multiprocessing.Pool(5) as pool:

        list(pool.imap(update_doc, collection.find()))

    print(time.time()-start_time)
