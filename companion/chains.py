from django.http import HttpResponse
import json
from companion.modules.chains.chains_model import Chain
from companion.modules.chains.chains_service import ChainsService



def index(request):
	if request.method == 'POST':
		body = json.loads(request.body)
		chain_id = ChainsService.run_chain(body['inputs'], body['title'])
		response_data = {}
		response_data['chain_id'] = chain_id
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	if request.method == 'GET':
		all_chains = Chain.objects()
		response_data = {}
		response_data['chains'] = json.loads(all_chains.to_json())
		return HttpResponse(json.dumps(response_data), content_type="application/json")

	return HttpResponse("Hello, world. You're at the chains index.")