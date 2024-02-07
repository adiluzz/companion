import multiprocessing
import os
from langchain.chains import LLMChain
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.llms import LlamaCpp
from langchain.tools import Tool, ShellTool
from langchain.agents import load_tools, initialize_agent
# from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.schema.output import LLMResult
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Any
from companion.modules.chains.chains_model import Chain
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from companion.modules.databases.services.create_vector_db import get_llama_embeddings
from companion.modules.databases.services.paths import create_temp_directories
from companion.modules.databases.services.s3_service import get_database_from_s3
from langchain.embeddings import LlamaCppEmbeddings


class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, chain_id) -> None:
        super().__init__()
        self.chain_id = chain_id

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID = None, **kwargs: Any) -> Any:
        Chain.objects(id=self.chain_id)[0].update(finished=datetime.now())

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        chain = Chain.objects(id=self.chain_id)[0]
        if 'chain' in chain:
            new_chain = chain.chain + token
            Chain.objects(id=self.chain_id)[0].update(chain=new_chain)
        else:
            Chain.objects(id=self.chain_id)[0].update(chain=token)

    def on_llm_error(self, error: Exception | KeyboardInterrupt, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        Chain().objects(id=self.chain_id).update(
            error={"error_time": datetime.now(), "error_text": error})


n_gpu_layers = 1
n_batch = 4096
n_ctx = 4096
tokens = 10000000


def get_callback_manager(chain_id):
    return CallbackManager([
        StreamingStdOutCallbackHandler(),
        MyCustomHandler(chain_id=chain_id)
    ])


def get_llm(chain_id):
    callback_manager = get_callback_manager(chain_id)
    path = os.environ['MODEL_PATH']
    llm = LlamaCpp(
        model_path=path,
        # n_gpu_layers=n_gpu_layers,
        # n_batch=n_batch,
        n_ctx=n_ctx,
        f16_kv=True,
        temperature=0.80,
        max_tokens=tokens,
        callback_manager=callback_manager,
        verbose=True,
    )

    return llm


def get_tools(llm):
    search = GoogleSearchAPIWrapper()

    def top10_results(query):
        return search.results(query, 10)

    tool = Tool(
        name="Google Search Snippets",
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
        func=top10_results,
    )
    shell_tool = ShellTool()

    tools = load_tools([
        # 'python_repl',
        'requests_all',
        'terminal',
        'wikipedia',
        'human'
    ], llm=llm)
    tools.append(tool)
    tools.append(shell_tool)
    return tools


def get_agent(tools, llm, export_to_csv):
    # if export_to_csv == True:
    # 	return create_csv_agent(
    # 		llm,
    # 		path='./temp/export.csv',
    # 		verbose=True,
    # 		# agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    # 	)
    # else:
    return initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


def run_chain(questions, prompt, chain_id, db_id):
    llm = get_llm(chain_id=chain_id)
    if db_id is not None:
        chain = run_qa_chain(
            db_id=db_id, question=questions[0], chain_id=chain_id)
        return chain
    else:
        tools = get_tools(llm)
        agent = get_agent(tools=tools, llm=llm, export_to_csv=False)
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        llm_chain.apply(questions)
        first_output = agent.run(llm_chain)
        return first_output


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


def retrieval_qa_chain(llm, prompt, db):
    return RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(
                                           search_kwargs={'k': 2}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt})


def qa_bot(llm, qa_prompt, db_id):
    llama_embeddings = LlamaCppEmbeddings(
        model_path=os.environ['MODEL_PATH'])
    create_temp_directories(db_id)
    databasde_location = get_database_from_s3(db_id)
    db = FAISS.load_local(databasde_location, llama_embeddings)
    qa = retrieval_qa_chain(llm, qa_prompt, db)
    return qa


def run_qa_chain(db_id, question, chain_id):
    try:
        print(chain_id)
        print('1')
        qa_prompt = custom_prompt()
        print('2')
        llm = get_llm(chain_id=chain_id)
        print('3')
        qa_result = qa_bot(llm=llm, qa_prompt=qa_prompt, db_id=db_id)
        print('4')
        print(question['question'])
        prompt = ChatPromptTemplate.from_template(
            question['question'])
        print('5')
        chain = qa_result | prompt | llm
        print('6')
        response = chain.invoke(question['question'])
        print('7')
        return response
    except Exception as e:
        print(e)
