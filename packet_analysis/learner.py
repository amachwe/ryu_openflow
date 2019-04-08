import pymongo

MONGO_HOST = "192.168.0.19"
MONGO_PORT = 27017

mongo_client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet