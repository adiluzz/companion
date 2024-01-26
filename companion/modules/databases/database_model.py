from mongoengine import *
import datetime


class Database(DynamicDocument):
    name = StringField(required=True, max_length=200)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    finished = DateTimeField()
    chunks = IntField()
    documents = [ObjectIdField()]
    meta = {'allow_inheritance': True}
