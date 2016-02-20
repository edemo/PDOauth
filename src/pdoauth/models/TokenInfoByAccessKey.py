from sqlalchemy import Column, Integer, String
from pdoauth.app import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
import time
from pdoauth.ModelUtils import ModelUtils
from pdoauth.models.KeyData import KeyData


class DuplicateAccessKey(Exception):
    pass

class TokenInfoByAccessKey(db.Model, ModelUtils):
    __tablename__ = 'tokeninfo_by_access_key'
    id = Column(Integer,primary_key=True)
    tokeninfo_id = Column(Integer, ForeignKey('key_data.id'))
    tokeninfo = relationship(KeyData)
    access_key = Column(String, unique=True)
    expire_time = Column(Integer)

    @classmethod
    def find(klass, access_key, _called_at = None):
        if _called_at is None:
            _called_at = time.time()
        ret = klass.query.filter_by(access_key=access_key).first()
        if ret is not None and ret.expire_time <= int(_called_at):
            ret.rm()
            ret = None
        return ret
        
        
    @classmethod
    def new(cls, access_key, tokeninfo, expires_in):
        if cls.find(access_key):
            raise DuplicateAccessKey()
        tiba = cls(access_key, tokeninfo, expires_in)
        tiba.save()
        return tiba
    
    def __init__(self, access_key, tokeninfo, expires_in):
        self.access_key = access_key
        self.tokeninfo = tokeninfo
        self.expire_time = time.time() + expires_in

    @classmethod
    def removeAllForKey(cls, key):
        instances = cls.query.filter_by(access_key=key.access_key).all()
        for instance in instances:
            instance.rm()

KeyData.subscribe(TokenInfoByAccessKey.removeAllForKey, "pre_rm")