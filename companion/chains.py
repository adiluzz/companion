from django.http import HttpResponse
import json
from companion.modules.chains.chains_service import ChainsService



def index(request):
	if request.method == 'POST':
		body = json.loads(request.body)
		print(body['inputs'])
		ChainsService.run_chain(body['inputs'])
	return HttpResponse("Hello, world. You're at the chains index." + request.method)