import traceback
import json
from django.http import HttpResponse
from pydantic import ValidationError

from companion.modules.databases.databases_service import create_database, delete_database, get_all_databases, get_database_by_id
from companion.modules.databases.validations.database_validations import DatabaseRequest


def index(request, database_id=None):
    if request.method == 'GET':
        try:
            if database_id:
                database = get_database_by_id(database_id=database_id)
                if database is not None:
                    resposne_data = {}
                    resposne_data['database'] = database
                    return HttpResponse(json.dumps(resposne_data, default=str), content_type="application/json")
                else:
                    return HttpResponse('Database not found', status=400)
            else:
                dbs = get_all_databases()
                return HttpResponse(dbs, content_type="application/json")
        except Exception as e:
            print(e)
            traceback.print_exc()
            return HttpResponse('Unexpected error', status=400)

            
    if request.method == 'POST':
        body = json.loads(request.body)
        try:
            name = body.get('name', '')
            document_ids = body.get('document_ids', [])
            chunk_size = body.get('chunk_size', None)
            chunk_overlap = body.get('chunk_overlap', None)
            n_ctx = body.get('n_ctx', None)
            DatabaseRequest(document_ids=document_ids, name=name)
            database = create_database(document_ids=body['document_ids'], name=body['name'], chunk_size=chunk_size, chunk_overlap=chunk_overlap, n_ctx=n_ctx)
            return HttpResponse(database, content_type="application/json")
        except ValidationError as ve:
            error = ve.errors()[0]
            return HttpResponse(content=error.get('msg'), status=400)
        except Exception as error:
            print('::GOT ERROR IN POST DATABASE::')
            print(error)
            traceback.print_exc()
            return HttpResponse(content='Error while trying to create database' , status=400)
        

    if request.method == 'PUT':
        print('PUT')
        return HttpResponse('Success')
        

    if request.method == 'DELETE':
        ids = json.loads(request.body)
        for id in ids:
            delete_database(id)
        return HttpResponse('Success')
        

    return HttpResponse("Hello, world. You're at the databases index.")
