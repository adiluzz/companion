# Requires:
# pip install docarray tiktoken

import os
import multiprocessing
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings import LlamaCppEmbeddings
from langchain.prompts import ChatPromptTemplate
import os
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

n_ctx = 4096
hugginface_model = 'TheBloke/Llama-2-13B-chat-GGML'
tokens = 10000000


def custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    custom_prompt_template = """Use the following pieces of information to answer the users question.
    If you dont know the answer, just say that you dont know, dont try to make up an answer.

    Context: {context}
    Question: {question}

    Only return the helpful answer below and nothing else.
    Helpful and Caring answer:"""
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt


DATA_PATH = 'demodata/'
DB_FAISS_PATH = 'vectorstore/db_faiss'
hf_token = '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'
model_id = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings()


def get_llama_embeddings():
    embedding = LlamaCppEmbeddings(
        model_path=os.environ['MODEL_PATH'],
        n_threads=max(multiprocessing.cpu_count() - 1, 1),
        n_ctx=n_ctx)
    return embedding


def get_callback_manager():
    return CallbackManager([
        StreamingStdOutCallbackHandler()
    ])


def create_vector_db():
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


def retrieval_qa_chain(llm, prompt, db):
    return RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(
                                           search_kwargs={'k': 2}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt})


def qa_bot(llm, qa_prompt):
    llama_embeddings = get_llama_embeddings()
    db = FAISS.load_local(DB_FAISS_PATH, llama_embeddings)
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa


class LearnService:
    def run_qa_chain():
        create_vector_db()
        qa_prompt = custom_prompt()
        llm = get_llm()
        qa_result = qa_bot(llm=llm, qa_prompt=qa_prompt)
        question = "what did Adi Iluz do in 2020?"
        prompt = ChatPromptTemplate.from_template(
            question)
        chain = {"context": qa_result, "question": prompt
                 } | prompt | llm
        response = chain.invoke()
        return response


def get_llm():
    path = os.environ['MODEL_PATH']
    llm = LlamaCpp(
        model_path=path,
        # n_gpu_layers=n_gpu_layers,
        # n_batch=n_batch,
        n_ctx=n_ctx,
        f16_kv=True,
        temperature=0.1,
        max_tokens=tokens,
        callback_manager=get_callback_manager(),
        verbose=True,
    )
    return llm


if __name__ == "__main__":
    create_vector_db()
