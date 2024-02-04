from mongoengine import *
import datetime

class Chunk(EmbeddedDocument):
    time_printed = DateTimeField()
    ms_per_token = FloatField()
    chunk_total_time = FloatField()
    tokens = IntField()
    
class Database(DynamicDocument):
    name = StringField(required=True, max_length=200)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    finished = DateTimeField()
    total_chunks = IntField()
    chunks = ListField(EmbeddedDocumentField(Chunk))
    average_ms_per_token = FloatField()
    average_tokens_per_chunk = FloatField()
    average_chunk_total_time = FloatField()
    time_finished = DateTimeField()
    documents = [ObjectIdField()]
    meta = {'allow_inheritance': True}
