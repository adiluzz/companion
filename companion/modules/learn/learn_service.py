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


# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

class LearnService:
    def learn_from_file():
        # Embed text
        vectorstore = DocArrayInMemorySearch.from_texts(
            ["harrison worked at kensho and likes ice cream", "bears like to eat honey"],
            embedding=LlamaCppEmbeddings(model_path=os.environ['MODEL_PATH']),
        )
        # Store in database
        retriever = vectorstore.as_retriever()
        
        # Prepare template and llm
        template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        simple_template = "Answer this question: {question}"
        prompt = ChatPromptTemplate.from_template(simple_template)
        
        model = get_llm()

        # build and run chain
        chain = prompt | model | StrOutputParser()

        # runnable = RunnableSerializable({"question":"where did harrison work?"})
        chain.invoke({"question":"where did harrison work?"})

    def run_simple_chain():
        prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
        model = get_llm()
        # build and run chain
        chain = prompt | model
        chain.invoke({"topic":"pasta"})        

def get_llm():
    path = os.environ['MODEL_PATH']
    n_ctx = 4096
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


