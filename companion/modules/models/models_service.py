import os
from langchain import GoogleSearchAPIWrapper, LLMChain
from langchain.llms import LlamaCpp
from langchain.tools import Tool, tool
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.schema.output import LLMResult
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Any



class MyCustomHandler(BaseCallbackHandler):
	def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID = None, **kwargs: Any) -> Any:
		print(response)
	
	def on_llm_new_token(self, token: str, **kwargs) -> None:
		with open(os.getcwd() + '/temp/text.txt', "a") as file:
			file.write(token)


n_gpu_layers = 1
n_batch = 2048
n_ctx = 512
tokens = 10*1000*1000

def get_callback_manager():
	return CallbackManager([
		StreamingStdOutCallbackHandler(), 
		MyCustomHandler()
	])

def get_llm():
	callback_manager = get_callback_manager()
	path = os.environ['MODEL_PATH']
	llm =LlamaCpp(
		model_path=path,
		# n_gpu_layers=n_gpu_layers,
		# n_batch=n_batch,
		# n_ctx=n_batch,
		f16_kv=True,
		temperature=0.75,
		max_tokens=tokens,
		callback_manager=callback_manager,
		verbose=True,
	)
	return llm

def get_tools(llm):
	search = GoogleSearchAPIWrapper()
	tool = Tool(
		name="Google Search",
		description="Search Google and return the first result.",
		func=search.run,
	)
	tools = load_tools([
		'python_repl',
		'requests_all',
		'terminal',
		# 'wikipedia',
		'human'
	], llm=llm)
	tools.append(tool)
	return tools

def get_agent(tools, llm):
	agent =  initialize_agent(
		tools, llm, agent="zero-shot-react-description", verbose=True)
	return agent

def run_chain(questions, prompt):
	llm = get_llm()
	tools = get_tools(llm)
	agent = get_agent(tools=tools, llm=llm)
	llm_chain = LLMChain(llm=llm, prompt=prompt)
	llm_chain.apply(questions)
	first_output = agent.run(llm_chain)
	return first_output

