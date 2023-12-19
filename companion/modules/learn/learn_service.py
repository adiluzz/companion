# Requires:
# pip install docarray tiktoken

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


# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_ctx = 4096 * 10

class LearnService:
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

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
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
        chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | model | output_parser
        print(chain)
        chain.invoke("where did harrison work?")

    def run_simple_chain():
        prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
        model = get_llm()
        # build and run chain
        chain = prompt | model 
        print(chain)    ## prints the chain pipeline
        chain.invoke({"topic":"ice cream"})

    def run_parallel_chain():
        prompt = ChatPromptTemplate.from_template("given this context: {context}, answer this question: {question}")
        model = get_llm()
        # build and run chain
        chain = (
            {"context": RunnablePassthrough, "question":RunnablePassthrough}
            | prompt
            | model 
            )
        print(chain)    ## prints the chain pipeline
        chain.invoke({"context":"harry is a lawyer who lives in Bronks", "question":"where does harry live?"})


def get_llm():
    path = os.environ['MODEL_PATH']
    tokens = 10000000

    llm = LlamaCpp(
            model_path=path,
            # n_gpu_layers=n_gpu_layers,
            # n_batch=n_batch,
            n_ctx=n_ctx,
            f16_kv=True,
            temperature=0.1,
            max_tokens=tokens,
            callback_manager=callback_manager,
            verbose=True,
	    )
    return llm


