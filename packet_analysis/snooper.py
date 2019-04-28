import sys
import socket
from pymongo import MongoClient
from bson import Binary
import datetime
import hashlib

MONGO_HOST = "192.168.0.19"
MONGO_PORT = 27017

mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
database = mongo_client.Packet_Snoop
collection = database.collection.Raw_Packet

print("Snooper with eth interface: {}".format(sys.argv[1]))

eth_intf = sys.argv[1]

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))

s.bind((eth_intf, 0))

# to track duplicate packets
pkt_store = set()

print("Running Packet Snoop")

while True:

	pkt = s.recv(65565)
	id = hashlib.md5(pkt).hexdigest()

	if not id in pkt_store:
		try:
			collection.insert_one({"_id": id, "date":
				datetime.datetime.utcnow(), "packet": Binary(pkt)})
		except:
			pass
		# to ensure we don't add duplicate packets
		pkt_store.add(id)
