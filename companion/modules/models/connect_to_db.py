import subprocess
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder
from pymongo_ssh import MongoSession
from mongoengine import connect
bastion_host = "44.204.129.77"
bastion_port = 22
bastion_user = "ubuntu"
private_key_path = "/home/adi_iluz/.ssh/id_rsa"
mongo_host = "10.0.2.137"
local_port = 27017
database_name = 'companion'
collection_name = 'chains'




def connect_to_db():
    with SSHTunnelForwarder(
        bastion_host,
        ssh_username=bastion_user,
        ssh_pkey=private_key_path,
        remote_bind_address=(mongo_host, local_port)
    ) as tunnel:
        # Construct MongoDB URI with local port
        print(tunnel.ssh_host)
        mongo_uri = f"mongodb://{tunnel.local_bind_host}:{tunnel.local_bind_port}/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
        print(mongo_uri)
        # Connect to MongoDB using pymongo
        client = MongoClient(mongo_uri)

        # Example: Access a MongoDB database and collection
        db = client["companion"]
        collection = db.chains
        all_chaines = collection.find()
        print(all_chaines)
        for document in all_chaines:
            print(document)
