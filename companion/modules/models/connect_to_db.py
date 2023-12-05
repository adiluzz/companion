import os
import mongoengine
from sshtunnel import SSHTunnelForwarder


def connect_to_db():
    bastion_host = os.environ.get('BASTION_HOST')
    bastion_user = os.environ.get('BASTION_USER')
    private_key_path = os.environ.get('PRIVATE_KEY_PATH')
    mongo_host = os.environ.get('MONGO_HOST')
    local_port = os.environ.get('LOCAL_MONGO_PORT')
    database_name = "companion"
    if bastion_host is not None:
        tunnel =  SSHTunnelForwarder(
            bastion_host,
            ssh_username=bastion_user,
            ssh_pkey=private_key_path,
            remote_bind_address=(mongo_host, int(local_port))
        )
        tunnel.start()
        mongo_uri = f"mongodb://{tunnel.local_bind_host}:{tunnel.local_bind_port}/?readPreference=primary&directConnection=true"
        mongoengine.connect(host=mongo_uri, db=database_name)
    else:
        mongoengine.connect(host="mongodb://localhost:27017", db=database_name)
