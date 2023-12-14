import copy
from django.http import HttpResponse
import json
from companion.modules.chains.chains_model import Chain
from companion.modules.chains.chains_service import ChainsService



def index(request, chain_id):
    if request.method == 'GET':
        chain = Chain.objects(pk=chain_id)
        response_data = {}
        response_data['chain'] = json.loads(chain[0].to_json())
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    
    if request.method == 'DELETE':
        chain = Chain.objects(pk=chain_id)
        chain_to_return = copy.deepcopy(chain[0])
        chain.delete()
        response_data = {}
        response_data['chain'] = json.loads(chain_to_return.to_json())
        return HttpResponse(json.dumps(response_data), content_type="application/json")
	

    return HttpResponse("Hello, world. You're at the chains index.")