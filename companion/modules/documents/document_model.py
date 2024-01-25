from mongoengine import *
import datetime

class InputDocument(DynamicDocument):
    name = StringField(required=True, max_length=200)
    type = StringField(regex='pdf|txt', required=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    finished = DateTimeField()
    chunks=IntField()
    meta = {'allow_inheritance': True}