temp_directory = 'temp/documents'

def get_local_directory_by_id(id):
    return f"{temp_directory}/{id}/"


def get_local_path_by_id(id, type):
    return f"{get_local_directory_by_id(id)}{id}.{type}"


def get_documents_paths(document_id, type):
    paths = {}
    paths['temp_directory'] = temp_directory
    paths['base'] = get_local_directory_by_id(document_id)
    paths['file_location'] = get_local_path_by_id(id=document_id, type=type)
    return paths