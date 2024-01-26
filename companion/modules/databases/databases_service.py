

from companion.modules.databases.database_model import Database


def create_database(document_ids, name):
    db = Database()
    db.documents = document_ids
    db.name = name
    db.save()
    
    
def get_database_by_id(id):
    db = Database.objects(id=id)
    if db[0]:
        return db[0]
    else:
        return None
    
def get_all_databases():
    try:
        dbs = Database.objects()
        print(dbs.to_json())
        return dbs.to_json()
    except Exception as e:
        print(e)
        raise e
    