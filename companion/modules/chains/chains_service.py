from langchain import PromptTemplate
import os
from companion.modules.models.models_service import run_chain as run_chain_service
from companion.modules.chains.chains_model import Chain

class ChainsService:

	def run_chain(chain_data):
		template = """
  			Question: {question}. 
     		"""
		prompt = PromptTemplate(
			template=template, input_variables=["question"])
		created_chain = Chain()
		created_chain.name = 'No Name'
		created_chain.save()
		print("created_chain" + created_chain.to_json()['_id'])
		run_chain_service(questions=chain_data, prompt=prompt)


