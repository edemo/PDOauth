from sqlalchemy import Column, String
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
import uuid

class NotUnique(Exception):
    pass

class NonHttpsRedirectUri(Exception):
    pass

class Application(db.Model, ModelUtils):
    __tablename__ = 'application'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    secret = Column(String(14))
    redirect_uri = Column(String)

    @classmethod
    def get(klass, client_id):
        return klass.query.get(client_id)
                         

    @classmethod
    def find(klass, name, secret, redirect_uri):
        return klass.query.filter_by(name=name).first()

    @classmethod
    def new(klass, name, secret, redirect_uri):
        existing = klass.find(name,secret, redirect_uri)
        if existing:
            raise NotUnique("already existing application")
        ret = klass(name,secret,redirect_uri)
        ret.save()
        return ret

    def __init__(self, name, secret, redirect_uri):
        self.id=unicode(uuid.uuid4())
        self.name = name
        self.secret = secret
        if not redirect_uri.startswith("https://"):
            raise NonHttpsRedirectUri(redirect_uri)
        self.redirect_uri = redirect_uri
        
