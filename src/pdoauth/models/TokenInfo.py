from sqlalchemy import Column, Integer, String
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils

class TokenInfo(db.Model, ModelUtils):
    __tablename__ = 'tokeninfo'
    id = Column(Integer, primary_key=True)
    refresh_key = Column(String, unique=True)
    
    @classmethod
    def find(klass, refresh_key):
        return klass.query.filter_by(refresh_key=refresh_key).first()
        
    @classmethod
    def new(cls, refresh_key):
        tokeninfo=cls.find(refresh_key)
        if tokeninfo is None:
            tokeninfo = cls(refresh_key)
            tokeninfo.save()
        return tokeninfo
    
    def __init__(self, refresh_key):
        self.refresh_key = refresh_key
    
    
