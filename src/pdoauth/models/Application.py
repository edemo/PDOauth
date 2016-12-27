from sqlalchemy import Column, String, Boolean
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
import uuid
from sqlalchemy.sql.sqltypes import Integer

class NotUnique(Exception):
    pass

class NonHttpsRedirectUri(Exception):
    pass

class Application(db.Model, ModelUtils):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    appid = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True)
    secret = Column(String)
    redirect_uri = Column(String)
    can_email = Column(Boolean)

    @classmethod
    def get(klass, client_id):
        return klass.query.filter_by(appid=client_id).first()
                         

    @classmethod
    def find(klass, name):
        return klass.query.filter_by(name=name).first()

    @classmethod
    def new(klass, name, secret, redirect_uri):
        existing = klass.find(name)
        if existing:
            raise NotUnique("already existing application")
        ret = klass(name,secret,redirect_uri)
        ret.save()
        return ret

    def __init__(self, name, secret, redirect_uri):
        self.appid=uuid.uuid4().hex
        self.name = name
        self.secret = secret
        if not redirect_uri.startswith("https://"):
            raise NonHttpsRedirectUri(redirect_uri)
        self.redirect_uri = redirect_uri
        self.can_email = False

    
    @classmethod
    def all(cls):
        return cls.query.all()
    
    
