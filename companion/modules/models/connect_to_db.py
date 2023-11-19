import os
import mongoengine
from mongoengine import *
from sshtunnel import SSHTunnelForwarder


def connect_to_db():
    bastion_host = os.environ['BASTION_HOST']
    bastion_user = os.environ['BASTION_USER']
    private_key_path = os.environ['PRIVATE_KEY_PATH']
    mongo_host = os.environ['MONGO_HOST']
    local_port = int(os.environ['LOCAL_MONGO_PORT'])
    database_name = os.environ['DB_NAME']
    tunnel =  SSHTunnelForwarder(
        bastion_host,
        ssh_username=bastion_user,
        ssh_pkey=private_key_path,
        remote_bind_address=(mongo_host, local_port)
    )
    tunnel.start()
    mongo_uri = f"mongodb://{tunnel.local_bind_host}:{tunnel.local_bind_port}/?readPreference=primary&directConnection=true"
    mongoengine.connect(host=mongo_uri, db=database_name)
