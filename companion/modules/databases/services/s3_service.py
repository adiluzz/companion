import os
import shutil
import boto3

from companion.modules.databases.services.paths import get_temp_paths


s3 = boto3.resource('s3', region_name='il-central-1')
bucket_name = 'companion-databases'
bucket = s3.Bucket(bucket_name)


def get_remote_database_path(database_id):
    remote_path = f'{database_id}/{database_id}.zip'
    return remote_path


def save_database_to_s3(local_path, database_id):
    remote_path = get_remote_database_path(database_id=database_id)
    bucket.upload_file(local_path, remote_path)


def remove_database_from_s3(db_id):
    bucket.objects.filter(Prefix=db_id).delete()

def get_database_from_s3(database_id):
    remote_address = get_remote_database_path(database_id=database_id)
    paths = get_temp_paths(database_id)
    obj = s3.Object(bucket_name, remote_address)
    temp_file = f'temp/{database_id}.zip'
    obj.download_file(Filename=temp_file)
    shutil.unpack_archive(temp_file, paths['base'])
    os.remove(temp_file)
    return paths['database']