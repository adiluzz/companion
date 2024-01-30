

import json
import os
import pathlib
import subprocess
from threading import Thread
import time
import boto3
from companion.modules.databases.database_model import Database
from companion.modules.databases.handlers.ErrorFileHandler import ErrorFileHandler
from companion.modules.databases.handlers.LogFileHandler import LogFileHandler
from companion.modules.databases.services.create_vector_db import get_splitted_text
from companion.modules.databases.services.paths import get_temp_paths
from companion.modules.databases.services.s3_service import remove_database_from_s3
from companion.modules.documents.documents_service import get_document_by_id, get_document_file
from companion.modules.documents.services.documents_paths import get_documents_paths
from shutil import copyfile
from watchdog.observers import Observer


n_ctx = 4096
bucket_name = 'companion-databases'
temp_directory = 'temp/databases'
s3 = boto3.resource('s3', region_name='il-central-1')
bucket_name = 'companion-databases'


def create_db_in_db(name, document_ids):
    db = Database()
    db.documents = document_ids
    db.name = name
    db.save()
    return db


def create_temp_directories(db_id):
    local_paths = get_temp_paths(db_id=db_id)
    paths = [
        local_paths['temp_directory'],
        local_paths['base'],
        local_paths['documents'],
        local_paths['database']
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


def get_document_in_database_temp(document_id, database_id):
    try:
        document = json.loads(get_document_by_id(id=document_id))
        document_path = get_document_file(id=document_id, ext=document['type'])
        local_paths = get_temp_paths(database_id)
        document_paths = get_documents_paths(
            document_id=document_id, type=document['type'])
        dest = f'{local_paths["documents"]}{document_id}.{document["type"]}'
        copyfile(document_path, dest)
        os.remove(path=document_path)
        os.rmdir(document_paths['base'])
        return document_path
    except Exception as e:
        print(e)
        raise e


def create_database_process(db, chunk_size, chunk_overlap):
    local_paths = get_temp_paths(db.id)
    with open(local_paths['log_file'], "w+") as log, open(local_paths['error_file'], "w+") as error:
        curent_file_path = pathlib.Path(__file__).parent.resolve()
        file_path = f'{curent_file_path}/services/create_vector_db.py'
        subprocess.Popen(['python', file_path, local_paths['documents'],
                          local_paths['database'], str(chunk_size), str(chunk_overlap)], stdout=log, stderr=error)
        observer = Observer()
        observer.schedule(
            event_handler=ErrorFileHandler(db=db),  path=local_paths['error_file'])
        observer.schedule(event_handler=LogFileHandler(
            db=db), path=local_paths['log_file'])
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def get_documents_to_temp_folder(document_ids, db_id):
    documents_paths = []
    for doc in document_ids:
        document_path = get_document_in_database_temp(
            document_id=doc, database_id=db_id)
        documents_paths.append(document_path)
    return documents_paths


def create_database(document_ids, name, chunk_size, chunk_overlap):
    db = create_db_in_db(name=name, document_ids=document_ids)
    create_temp_directories(db.id)
    local_paths = get_temp_paths(db_id=db.id)
    get_documents_to_temp_folder(document_ids=document_ids, db_id=db.id)
    total_chunks = len(get_splitted_text(local_paths['documents'], chunk_size, chunk_overlap))
    db.total_chunks = total_chunks
    db.save()
    thread = Thread(target=create_database_process, args=(db, chunk_size, chunk_overlap,))
    thread.start()
    return


def get_database_by_id(id):
    db = Database.objects(id=id)
    if db[0]:
        return db[0]
    else:
        return None


def get_all_databases():
    try:
        dbs = Database.objects()
        return dbs.to_json()
    except Exception as e:
        print(e)
        raise e


def delete_database(id):
    database = Database.objects(pk=id).first()
    remove_database_from_s3(db_id=id)
    database.delete()
