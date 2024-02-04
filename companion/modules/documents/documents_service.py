import os
import boto3
from django import forms

from companion.modules.documents.document_model import InputDocument
from companion.modules.documents.services.documents_paths import get_local_directory_by_id, get_local_path_by_id

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

def remove_document_from_s3(document_id, extension):
    remote_path = get_remote_file_address(id=document_id, ext=extension)
    s3.Object(bucket_name, remote_path).delete()


def save_file(file, id, type):
    base_path = get_local_directory_by_id(id=id)
    path = get_local_path_by_id(id=id, type=type)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
        save_document_to_s3(document_id=id, local_path=path, extension=type)
        os.remove(path)


def save_document(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        name = form.data['name']
        existing_document = get_document_by_name(name=name)
        if existing_document:
            raise Exception('A Document with the same name already exists')
        type = form.data['type']
        try:
            doc = InputDocument()
            doc.name = name
            doc.type = type
            doc.save()
            save_file(
                file=request.FILES['file'], id=doc.id, type=type)
        except Exception as e:
            raise e


def get_documents():
    docs = InputDocument.objects()
    return docs.to_json()


def get_document_file(id, ext):
    try:
        remote_address = get_remote_file_address(id=id, ext=ext)
        local_dir = get_local_directory_by_id(id=id)
        local_address = get_local_path_by_id(id=id, type=ext)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        obj = s3.Object(bucket_name, remote_address)
        obj.download_file(Filename=local_address)
        return local_address
    except Exception as e:
        print(e)
        raise e


def get_document_by_id(id):
    document_from_db = InputDocument.objects(id=id).first()
    if document_from_db is not None:
        return document_from_db.to_json()
    return document_from_db


def get_document_by_name(name):
    document_from_db = InputDocument.objects(name=name)
    if len(document_from_db) > 0:
        return document_from_db[0].to_json()
    else:
        return None

def update_document_name(document_id, new_name):
    doc = InputDocument.objects(id=document_id)[0]
    doc.name = new_name
    doc.save()
    return doc

def delete_document(document_id):
    doc = InputDocument.objects(id=document_id)[0]
    remove_document_from_s3(document_id=document_id, extension=doc.type)
    doc.delete()
    