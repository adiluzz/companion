# Requires:
# pip install docarray tiktoken

import os
import multiprocessing
from langchain.chains import LLMChain
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.llms import LlamaCpp
from langchain.tools import Tool, tool, ShellTool
from langchain.agents import load_tools, initialize_agent
#from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.schema.output import LLMResult
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Any, Optional, Union
from companion.modules.chains.chains_model import Chain
from datetime import date, datetime


from langchain.embeddings import LlamaCppEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import DocArrayInMemorySearch
# from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import StructuredOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableSerializable
# for llm
import os
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
import bs4
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Callbacks support token-wise streaming
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
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
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
 	
    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID = None, **kwargs: Any) -> Any:
        print('CHAIN END')
	
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # print(f"My custom handler, token: {token}")# Create vector database
        print(token)
        
    def on_llm_error(self, error: Exception | KeyboardInterrupt, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        print('ERROR' + error)
            

def get_llama_embeddings():
    path = os.environ['MODEL_PATH']
    print('PATH IS:::'  + path)
    embedding = LlamaCppEmbeddings(
        model_path=os.environ['MODEL_PATH'], 
        n_threads=max(multiprocessing.cpu_count() - 1, 1),
        n_ctx=n_ctx)
    return embedding

def get_callback_manager():
	return CallbackManager([
		StreamingStdOutCallbackHandler(), 
		# MyCustomHandler()
	])

# def FunctionHandler(BaseCallbackHandler):
#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         print(f"My custom handler, token: {token}")# Create vector database


def create_vector_db():
    print("CREATING DATABASE")
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print("FINISHED DATABASE 1")
    llama_embeddings = get_llama_embeddings()
    db = FAISS.from_documents(texts, llama_embeddings)

    print("FINISHED DATABASE 2")
    db.save_local(DB_FAISS_PATH)
    print("FINISHED DATABASE 3")
    return db


def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type='stuff',
                                           retriever=db.as_retriever(
                                               search_kwargs={'k': 2}),
                                           return_source_documents=True,
                                           chain_type_kwargs={'prompt': prompt})
    return qa_chain


def qa_bot(llm):
    print('2')
    llama_embeddings = get_llama_embeddings()
    db = FAISS.load_local(DB_FAISS_PATH, llama_embeddings)
    print('4')
    qa_prompt = custom_prompt()
    
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)
    print('5')
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    print('6')
    # splits = text_splitter.split_documents(docs)
    print('7')
    
    # vectorstore = Chroma.from_documents(documents=splits, embedding=LlamaCppEmbeddings(
    #     model_path=os.environ['MODEL_PATH'],
    #     n_ctx=n_ctx
    # ))
    print('8')
    
    # retriever = vectorstore.as_retriever()
    
    print('9')

    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa


class LearnService:

    def run_qa_chain():
        print("START PROCESS")
        db = create_vector_db()
        print("START PROCESS 2")
        llm = get_llm()
        qa_result = qa_bot(llm=llm)
        print("START PROCESS 3")
        question = "what did Adi Iluz do in 2020?"
        prompt = ChatPromptTemplate.from_template(
            question)
        chain = {"context": qa_result, "question": prompt
                 } | prompt | llm

        # prompt = "what did adi do in 2017?"
        
        response = chain.invoke(question)
        # response = qa_result.run(prompt,return_only_outputs=True)
        # response = qa_result.arun(prompt=prompt, return_only_outputs=True, callbacks=[MyCustomHandler()])
        
        
        # response = qa_result.arun("what did adi do in 2017?")
        print("START PROCESS 4")
        print(response)
        return response

    def learn_from_file():
        # Embed text
        loader = WebBaseLoader(
            web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("post-content", "post-title", "post-header")
                )
            ),
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=LlamaCppEmbeddings(
            model_path=os.environ['MODEL_PATH'],
            n_ctx=n_ctx
        ))
        retriever = vectorstore.as_retriever()

        # Prepare template and llm
        template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        model = get_llm()
        output_parser = StrOutputParser()
        chain = {"context": retriever, "question": RunnablePassthrough()
                 } | prompt | model | output_parser
        print(chain)
        chain.invoke("where did harrison work?")

    def run_simple_chain():
        prompt = ChatPromptTemplate.from_template(
            "tell me a short joke about {topic}")
        model = get_llm()
        # build and run chain
        chain = prompt | model
        print(chain)  # prints the chain pipeline
        chain.invoke({"topic": "ice cream"})

    def run_parallel_chain():
        prompt = ChatPromptTemplate.from_template(
            "given this context: {context}, answer this question: {question}")
        model = get_llm()
        # build and run chain
        chain = (
            {"context": RunnablePassthrough, "question": RunnablePassthrough}
            | prompt
            | model
        )
        print(chain)  # prints the chain pipeline
        chain.invoke({"context": "harry is a lawyer who lives in Bronks",
                     "question": "where does harry live?"})


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


def load_llm():
    # Load the locally downloaded model here
    llm = CTransformers(
        model=hugginface_model,
        model_type="llama",
        max_new_tokens=512 * 8,
        temperature=0.75,
        callback_manager=get_callback_manager(),
        verbose=True,
        n_ctx=n_ctx,
        f16_kv=True,
        max_tokens=tokens,
    )
    return llm


if __name__ == "__main__":
    create_vector_db()
