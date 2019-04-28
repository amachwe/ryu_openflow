from pymongo import mongo_client
import binascii

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

def write_row_to_result_file(fh, doc, cardinal, count, raw=False):
    y = doc["Y"]
    l = doc["Length"]
    x = binascii.hexlify(doc["packet"]).decode('utf-8')

    if raw:
        row = [str(int(i, 16)) for i in x]
    else:
        row = [str(round(int(i, 16) / 15, 2)) for i in x]

    for i in range(len(row), HEX_MTU):
        row.append("0")

    c = build_cardinal(cardinal, y)
    row.extend([str(c), y, str(l)])

    count += 1

    if count % 10000 == 0:
        print(count)

    txt = ','.join(row)

    fh.write(txt)
    fh.write("\n")


def build_full_results(filename):
    with open(filename, "w") as fh:
        cardinal = {}
        count = 0
        for doc in collection.find():
           write_row_to_result_file(fh, doc, cardinal, count)


def build_subset(filename, max_per_class=10000, raw=False):

    with open(filename, "w") as fh:
        cardinal = {}
        count = 0

        pipeline = [
            {
                "$group" : {
                    "_id": "$Y",
                    "count": {
                        "$sum": 1
                    }
                }
            }
        ]

        res = collection.aggregate(pipeline)
        fh.write(",".join([f"c{i}" for i in range(0, HEX_MTU)]))
        fh.write(",Y,Y_text,length")
        fh.write("\n")
        for doc in res:
            for cls_doc in collection.find({"Y": doc["_id"]}).limit(max_per_class):
                    write_row_to_result_file(fh, cls_doc, cardinal, count, raw=raw)








if __name__ == "__main__":
    #build_full_results("packet_data.csv")
    build_subset("packet_data_reduced_20k_raw.csv", max_per_class=20000, raw=True)








