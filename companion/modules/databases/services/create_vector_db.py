import os
import multiprocessing
import sys
from langchain.embeddings import LlamaCppEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

n_ctx = 4096
bucket_name = 'companion-databases'

def get_splitted_text(path, chunk_size, chunk_overlap):
    if chunk_size is None or 'None':
        chunk_size = 200
    if chunk_overlap is None or 'None':
        chunk_overlap = 50
    loader = DirectoryLoader(path=path,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                   chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    return texts
    
def get_llama_embeddings():
    embedding = LlamaCppEmbeddings(
        model_path=os.environ['MODEL_PATH'],
        n_threads=max(multiprocessing.cpu_count() - 1, 1),
        n_ctx=n_ctx)
    return embedding

def create_vector_db(source, dest, chunk_size, chunk_overlap):
    texts = get_splitted_text(path=source, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    llama_embeddings = get_llama_embeddings()
    db = FAISS.from_documents(texts, llama_embeddings)
    db.save_local(dest)
    return db


if __name__ == "__main__":
    args = sys.argv[1:]
    source = args[0]
    dest = args[1]
    chunk_size = args[2]
    chunk_overlap = args[3]
    try:
        db = create_vector_db(source=source, dest=dest, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print('::FINISHED PROCESS::')
        sys.exit(0)
    except SystemExit as sys_exit:
        print('Caught the SystemExit exception::')
        print(str(sys_exit))
        raise sys_exit
    except Exception as e:
        print(e)
        raise e
    
