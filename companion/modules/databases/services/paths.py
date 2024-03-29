import os


temp_directory = 'temp/databases'

def get_temp_paths(db_id):
    paths = {}
    paths['temp_directory'] = temp_directory
    paths['base'] = f'{temp_directory}/{db_id}/'
    paths['documents'] = f'{paths["base"]}documents/'
    paths['database'] = f'{paths["base"]}database/'
    paths['database_zip_file_name'] = 'output'
    paths['database_zip_format'] = 'zip'
    paths['database_zip_name'] = f'{paths["base"]}{paths["database_zip_file_name"]}'
    paths['database_zip_path'] = f'{paths["database_zip_name"]}.{paths["database_zip_format"]}'
    paths['log_file'] = f'{paths["database"]}log.txt'
    paths['error_file'] = f'{paths["database"]}error.txt'
    return paths

def create_temp_directories(db_id):
    local_paths = get_temp_paths(db_id=db_id)
    paths = [
        local_paths['temp_directory'],
        local_paths['base'],
        local_paths['documents'],
        local_paths['database']
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
