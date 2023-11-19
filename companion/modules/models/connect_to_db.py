import mongoengine
from mongoengine import *
from sshtunnel import SSHTunnelForwarder

bastion_host = "44.204.129.77"
bastion_user = "ubuntu"
private_key_path = "/home/adi_iluz/.ssh/id_rsa"
mongo_host = "10.0.2.137"
local_port = 27017
database_name = 'companion'

def connect_to_db():
    tunnel =  SSHTunnelForwarder(
        bastion_host,
        ssh_username=bastion_user,
        ssh_pkey=private_key_path,
        remote_bind_address=(mongo_host, local_port)
    )
    tunnel.start()
    mongo_uri = f"mongodb://{tunnel.local_bind_host}:{tunnel.local_bind_port}/?readPreference=primary&directConnection=true"
    mongoengine.connect(host=mongo_uri, db=database_name)
