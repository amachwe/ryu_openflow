from pymongo import mongo_client
import binascii
import multiprocessing
from matplotlib import pyplot as plt
import pandas as pd

BITS_MTU = 1522*8
HEX_MTU = 1522*2

mc = mongo_client.MongoClient("localhost", 27017)
collection = mc["Packet_Snoop"].collection.Raw_Packet


def build_cardinal(cardinal, y):

    c = cardinal.get(y)

    if c:
        return c
    else:
        id = len(cardinal.keys())+1
        cardinal[y] = id
        return id



if __name__ == "__main__":

    cardinal = {}
    count = 0

    with open("packet_data.csv", "w") as fh:
        for doc in collection.find():
            y = doc["Y"]
            l = doc["Length"]
            x = binascii.hexlify(doc["packet"]).decode('utf-8')

            row = [str(round(int(i, 16)/15,2)) for i in x]

            for i in range(len(row), HEX_MTU):
                row.append("0")


            c =build_cardinal(cardinal, y)
            row.extend([str(c), y, str(l)])

            count += 1

            if count % 10000 == 0:
                print(count)

            txt = ','.join(row)

            fh.write(txt)
            fh.write("\n")





