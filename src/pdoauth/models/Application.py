from sqlalchemy import Column, String, Integer
from pdoauth.app import db

class NotUnique(Exception):
    pass

class NonHttpsRedirectUri(Exception):
    pass

class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    secret = Column(String(14))
    redirect_uri = Column(String)

    @classmethod
    def find(klass, client_id):
        return klass.query.get(client_id)
                         

    @classmethod
    def getExisting(klass, name, secret, redirect_uri):
        res = klass.query.filter_by(name=name).first()
        if res is not None:
            if res.secret != secret:
                raise NotUnique("secret differs")
            if res.redirect_uri != redirect_uri:
                raise NotUnique("redirect_uri differs")
            return res

    @classmethod
    def new(klass, name, secret, redirect_uri):
        existing = klass.getExisting(name,secret, redirect_uri)
        if existing:
            return existing
        return klass(name,secret,redirect_uri)

    def __init__(self, name, secret, redirect_uri):
        self.name = name
        self.secret = secret
        if not redirect_uri.startswith("https://"):
            raise NonHttpsRedirectUri(redirect_uri)
        self.redirect_uri = redirect_uri
        
