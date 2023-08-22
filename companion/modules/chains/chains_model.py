import datetime
from mongoengine import *

connect('comapnion')


class Chain(Document):
    name = StringField(required=True, max_length=200)
    created = DateTimeField(default=datetime.datetime.utcnow)
    chain = StringField()
    meta = {'allow_inheritance': True}