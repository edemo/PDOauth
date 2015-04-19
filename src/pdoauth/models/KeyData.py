from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils

class KeyData(db.Model, ModelUtils):
    __tablename__ = 'key_data'
    id = Column(Integer,primary_key=True)
    client_id = Column(String)
    user_id = Column(String)
    access_key = Column(String)
    refresh_key = Column(String)

    
    @classmethod
    def new(cls, client_id, user_id, access_key, refresh_key):
        keyData = cls.find(client_id, user_id)
        if keyData is None:
            keyData = cls(client_id, user_id, access_key, refresh_key)
            keyData.save()
        return keyData

    
    @classmethod
    def find(cls, client_id, user_id):
        return cls.query.filter_by(client_id=client_id, user_id = user_id).first()
    
    def __init__(self, client_id, user_id, access_key, refresh_key):
        self.client_id = client_id
        self.access_key = access_key
        self.user_id = user_id
        self.refresh_key = refresh_key
    
    
    



