from sqlalchemy import Column, String, Integer
from pdoauth.app import db
import random
import string


class NotUnique(Exception):
    pass

class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    secret = Column(String(14))

    @classmethod
    def find(klass, client_id):
        return klass.query.get(client_id)
                         

    @classmethod
    def getExisting(klass, name, secret):
        res = klass.query.filter_by(name=name).first()
        if res is not None:
            if res.secret == secret:
                return res
            else:
                raise NotUnique("secret differs")

    @classmethod
    def new(klass, name, secret, theid=None):
        existing = klass.getExisting(name,secret)
        if existing:
            return existing
        return klass(name,secret,theid)

    def __init__(self,name, secret, theid=None):
        self.name = name
        self.secret = secret
        
