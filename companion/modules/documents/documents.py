import os
from django import forms
from django.http import FileResponse, HttpResponse
import json
import base64


from companion.modules.documents.documents_service import get_document_by_id, get_document_file, get_documents, save_document


class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    type = forms.CharField(max_length=10, required=True)
    file = forms.FileField(required=True)


def handle_uploaded_file_old(f):
    with open("Adi.pdf", "wb+") as destination:
        for chunk in f.chunks():
            print(chunk)
            destination.write(chunk)


def handle_uploaded_file(file, name, type):
    print('START')
    directory = 'temp/documents'
    path = f"{directory}/{name}.{type}"
    print(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def index(request, document_id=None, file=None):
    print('HELLO')
    if request.method == 'GET':
        if document_id:
            print('HAS DOC_ID'+ document_id)
            doc = get_document_by_id(document_id)
            print(doc)
            if file:
                file_data = get_document_file(id=document_id, ext='pdf')
                with open(file_data, 'rb') as pdf:
                    data = base64.b64encode(pdf.read())
                    response = HttpResponse(data,content_type='application/pdf')
                    # response['Content-Disposition'] = 'filename=document.pdf'
                    return response
                # return FileResponse(file_data, content_type='application/pdf')

                # response = HttpResponse(file_data, content_type='application/pdf')
                # response['Content-Disposition'] = 'attachment; filename="file.pdf"'
                # return response
                # return HttpResponse(fil, content_type="application/json")
                
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
            return HttpResponse(e)
    return HttpResponse("Hello, world. You're at the documents index.")
