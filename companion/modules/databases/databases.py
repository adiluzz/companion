import json
from django.http import HttpResponse

from companion.modules.databases.databases_service import create_database, delete_database, get_all_databases, get_database_by_id


def index(request, database_id=None):
    if request.method == 'GET':
        if database_id:
            database = get_database_by_id(database_id=database_id)
            if database:
                return HttpResponse(database, content_type="application/json")
            else:
                return HttpResponse(None, content_type="application/json")
        else:
            dbs = get_all_databases()
            return HttpResponse(dbs, content_type="application/json")
            
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            database = create_database(document_ids=body['document_ids'], name=body['name'])
            return HttpResponse(database, content_type="application/json")
        except Exception as e:
            print(e)
            return HttpResponse(content=e, status=400)
            
        

    if request.method == 'PUT':
        print('PUT')
        return HttpResponse('Success')
        

    if request.method == 'DELETE':
        ids = json.loads(request.body)
        for id in ids:
            delete_database(id)
        return HttpResponse('Success')
        

    return HttpResponse("Hello, world. You're at the databases index.")
