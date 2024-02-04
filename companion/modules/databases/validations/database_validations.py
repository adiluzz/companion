from pydantic import BaseModel, model_validator, validator
from typing import List, Optional
from companion.modules.databases.database_model import Database
from companion.modules.documents.document_model import InputDocument


class DatabaseRequest(BaseModel):
    document_ids: List[str] = []
    name: Optional[str] = None



    @validator('name')
    def name_exists(cls, v):
        if v is None or v == '':
            raise ValueError('Please provide a Name for the database.')
        return v
    
    @validator('document_ids')
    def document_ids_exists(cls, v):
        if v is None or len(v) == 0:
            raise ValueError('Please provide a documents for the database.')
        return v

    @model_validator(mode="after")
    def name_exists_in_db(self):
        name = self.name
        try:
            database_with_the_same_name = Database.objects(name=name)
            assert len(database_with_the_same_name) == 0
            return self
        except Exception as e:
            raise ValueError('Database with this name exists')
        except:
            raise ValueError('Database with this name exists')
    
    @model_validator(mode="after")
    def documents_exist(self):
        document_ids = getattr(self, 'document_ids')
        try:
            for doc in document_ids:
                found_doc = InputDocument.objects(pk=doc).first()
                assert found_doc is not None
            return self
        except:
            ValueError('One or more documents do not exist for this database')
