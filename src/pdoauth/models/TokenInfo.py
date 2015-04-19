from sqlalchemy import Column, Integer, String
from pdoauth.app import db

class TokenInfo(db.Model):
    __tablename__ = 'tokeninfo'
    id = Column(Integer, primary_key=True)
    refresh_key = Column(String, unique=True)
    
    def save(self):
        session = db.session
        session.add(self)
        session.commit()

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
    
    
