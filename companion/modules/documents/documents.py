import json
import base64
import os
from django.http import HttpResponse, HttpResponseBadRequest
from companion.modules.documents.documents_service import delete_document, get_document_by_id, get_document_file, get_documents, save_document, update_document_name


def index(request, document_id=None, file=None):
    if request.method == 'GET':
        if document_id:
            doc = get_document_by_id(document_id)
            if file:
                file_data = get_document_file(id=document_id, ext='pdf')
                with open(file_data, 'rb') as pdf:
                    data = base64.b64encode(pdf.read())
                    os.remove(file_data)
                    return HttpResponse(data, content_type='application/pdf')
            else:
                return HttpResponse(doc, content_type="application/json")
        else:
            docs = get_documents()
            return HttpResponse(docs, content_type="application/json")

    if request.method == 'POST':
        try:
            save_document(request)
            return HttpResponse("Success")
        except Exception as e:
            print(e)
            return HttpResponseBadRequest(e)

    if request.method == 'PUT':
        try:
            body = json.loads(request.body)
            update_document_name(document_id=document_id,
                                 new_name=body['name'])
            return HttpResponse("Success")
        except Exception as e:
            print(e)
            return HttpResponse(e)

    if request.method == 'DELETE':
        try:
            if document_id:
                delete_document(document_id=doc)
            else:
                ids = json.loads(request.body)
                for doc in ids:
                    delete_document(document_id=doc)
            return HttpResponse("Success")
        except Exception as e:
            print(e)
            return HttpResponse(e)

    return HttpResponse("Hello, world. You're at the documents index.")
