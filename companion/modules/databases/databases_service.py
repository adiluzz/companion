

from companion.modules.databases.database_model import Database
import os
import multiprocessing
from langchain.embeddings import LlamaCppEmbeddings
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DB_FAISS_PATH = 'vectorstore/db_faiss'
DATA_PATH = 'demodata/'
n_ctx = 4096
bucket_name = 'companion-databases'

# def get_data_path(id):
    

def get_llama_embeddings():
    embedding = LlamaCppEmbeddings(
        model_path=os.environ['MODEL_PATH'],
        n_threads=max(multiprocessing.cpu_count() - 1, 1),
        n_ctx=n_ctx)
    return embedding

def create_vector_db(db):
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    llama_embeddings = get_llama_embeddings()
    db = FAISS.from_documents(texts, llama_embeddings)
    db.save_local(DB_FAISS_PATH)
    return db


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
    