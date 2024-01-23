from django.http import HttpResponse
import json
from companion.modules.chains.chains_model import Chain
from companion.modules.chains.chains_service import ChainsService
from companion.modules.learn.learn_service import LearnService



def index(request):
	if request.method == 'POST':
		response = LearnService.run_qa_chain()
		return HttpResponse('Success', content_type="application/json")
	
	return HttpResponse("Hello, world. You're at the learn index.")