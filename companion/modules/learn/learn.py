from django.http import HttpResponse
from companion.modules.learn.learn_service import LearnService


def index(request):
    if request.method == 'POST':
        response = LearnService.run_qa_chain()
        return HttpResponse('Success', content_type="application/json")

    return HttpResponse("Hello, world. You're at the learn index.")
