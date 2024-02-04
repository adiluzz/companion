import boto3


s3 = boto3.resource('s3', region_name='il-central-1')
bucket_name = 'companion-databases'


def get_remote_database_path(database_id):
    remote_path = f'{database_id}/{database_id}.zip'
    return remote_path


def save_database_to_s3(local_path, database_id):
    remote_path = get_remote_database_path(database_id=database_id)
    s3.Bucket(bucket_name).upload_file(local_path, remote_path)


def remove_database_from_s3(db_id):
    bucket = s3.Bucket(bucket_name)
    bucket.objects.filter(Prefix=db_id).delete()
