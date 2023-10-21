import datetime
from mongoengine import *

connect('comapnion')

class ChainError(Document):
    error_time = DateTimeField()
    error_texr = StringField()

class Chain(DynamicDocument):
    title = StringField(required=True, max_length=200)
    created = DateTimeField(default=datetime.datetime.utcnow)
    finished = DateTimeField()
    error = ChainError()
    chain = StringField()
    meta = {'allow_inheritance': True}