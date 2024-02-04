
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from companion.modules.databases.database_model import Chunk, Database
from companion.modules.databases.services.chunks_service import get_chunks, get_database_average_from_chunks

class ErrorFileHandler(FileSystemEventHandler):
    def __init__(self, db):
        self.db = db

    def on_modified(self, event):
        # print(
        #     f'ErrorFileHandler event type: {event.event_type} path : {event.src_path} total chunk: {self.db["total_chunks"]}')
        database = Database.objects(pk=self.db.id).first()
        if database.time_finished is None:
            chunks = get_chunks(path=event.src_path)
            if chunks is not None:
                db = Database.objects(pk=self.db.id).first()
                if len(getattr(db, 'chunks')) < len(chunks) or getattr(db, 'chunks') is None:
                    last_chunk = chunks[len(chunks) - 1]
                    chunk = Chunk(
                        ms_per_token=last_chunk['ms_per_token'],
                        tokens=last_chunk['tokens'],
                        time_printed=datetime.datetime.now(),
                        chunk_total_time=last_chunk['chunk_total_time']
                    )
                    db.chunks.append(chunk)
                    averages = get_database_average_from_chunks(db.chunks)
                    db.average_tokens_per_chunk = averages['average_tokens_per_chunk']
                    db.average_ms_per_token = averages['average_ms_per_token']
                    db.average_chunk_total_time = averages['average_chunk_total_time']
                    db.save()

