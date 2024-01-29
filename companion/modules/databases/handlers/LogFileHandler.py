import datetime
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from companion.modules.databases.database_model import Database

from companion.modules.databases.services.paths import get_temp_paths
from companion.modules.databases.services.s3_service import save_database_to_s3

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, db):
        self.db = db
        self.finished = False

    def on_any_event(self, event):
        # print(
        #     f'LogFileHandler event type: {event.event_type} path : {event.src_path} total chunk: {self.db["total_chunks"]}')
        process_finisher = '::FINISHED PROCESS::'
        if self.finished == False:
            try:
                with open(event.src_path) as file:
                    data = file.read()
                    if process_finisher in data:
                        self.finished = True
                        local_paths = get_temp_paths(db_id=self.db.id)
                        shutil.make_archive(
                            local_paths["database_zip_name"],
                            local_paths['database_zip_format'],
                            local_paths['base'],
                        )
                        save_database_to_s3(
                            database_id=self.db.id, local_path=local_paths['database_zip_path'])
                        database = Database.objects(pk=self.db.id).first()
                        database['time_finished'] = datetime.datetime.now()
                        database.save()
                        time.sleep(30)
                        shutil.rmtree(local_paths['base'])
            except Exception as e:
                self.finished = False
                print(e)
                raise e
            except:
                self.finished = False
                print('ANY_EXCEPTION')
                raise 'ANY_EXCEPTION'

