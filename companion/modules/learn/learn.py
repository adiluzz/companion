from django.http import HttpResponse
from companion.modules.learn.learn_service import LearnService


def index(request):
    if request.method == 'POST':
        question = "what did Adi Iluz do in 2020?"
        LearnService.query_vectorstore(question=question)
        return HttpResponse('Success', content_type="application/json")

    return HttpResponse("Hello, world. You're at the learn index.")
