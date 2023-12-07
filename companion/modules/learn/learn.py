from django.http import HttpResponse
import json
from companion.modules.chains.chains_model import Chain
from companion.modules.chains.chains_service import ChainsService
from companion.modules.learn.learn_service import LearnService



def index(request):
	if request.method == 'POST':
		body = json.loads(request.body)
		print(body)
		chain_id = LearnService.learn_from_file("testPath")
		response_data = {}
		response_data['chain_id'] = chain_id
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	return HttpResponse("Hello, world. You're at the learn index.")