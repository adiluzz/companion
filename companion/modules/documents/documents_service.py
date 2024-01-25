import os
import boto3
from django import forms

from companion.modules.documents.document_model import InputDocument

s3 = boto3.resource('s3', region_name='il-central-1')
bucket_name = 'companion-documents'


class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    type = forms.CharField(max_length=10, required=True)
    file = forms.FileField(required=True)


def get_remote_file_address(id, ext):
    remote_path = f'{id}/{id}.{ext}'
    return remote_path


def save_document_to_s3(document_id, local_path, extension):
    remote_path = get_remote_file_address(id=document_id, ext=extension)
    s3.Bucket(bucket_name).upload_file(local_path, remote_path)


def save_file(file, id, type):
    directory = 'temp/documents'
    path = f"{directory}/{id}.{type}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
        save_document_to_s3(document_id=id, local_path=path, extension=type)


def save_document(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        name = form.data['name']
        type = form.data['type']
        doc = InputDocument()
        doc.name = name
        doc.type = type
        doc.save()
        try:
            save_file(
                file=request.FILES['file'], id=doc.id, type=type)
        except Exception as e:
            print(e)


def get_documents():
    docs = InputDocument.objects()
    return docs.to_json()


def get_document_file(id, ext):
    try:
        remote_address = get_remote_file_address(id=id, ext=ext)
        local_address = f'temp/{id}.{ext}'
        obj = s3.Object(bucket_name, remote_address)
        obj.download_file(Filename=local_address)
        return local_address
    except Exception as e:
        print(e)


def get_document_by_id(id):
    document_from_db = InputDocument.objects(id=id)[0]
    return document_from_db.to_json()

def update_document_name(document_id, new_name):
    doc = InputDocument.objects(id=document_id)[0]
    doc.name = new_name
    doc.save()
    return doc