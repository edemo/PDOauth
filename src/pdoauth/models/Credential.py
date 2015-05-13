from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.orm import relationship
from pdoauth.models.User import User
import time


class Credential(db.Model, ModelUtils):
    __tablename__ = 'credential'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    credentialType = Column(String)
    identifier = Column(String)
    secret = Column(String)

    def __init__(self, user, credentialType, identifier, secret):
        self.user = user
        self.credentialType = credentialType
        self.identifier = identifier
        self.secret = secret
    
    @classmethod
    def get(cls, credentialType, identifier):
        return Credential.query.filter_by(credentialType = credentialType, identifier = identifier).first()

    @classmethod
    def getByUser(cls, user, credentialType=None):
        if credentialType is None:
            return Credential.query.filter_by(user=user).all()
        return Credential.query.filter_by(user=user, credentialType=credentialType).first()
    
    @classmethod
    def new(cls, user, credentialType, identifier, secret):
        oldcred = cls.get(credentialType, identifier)
        if oldcred is not None:
            return None
        cred = cls(user, credentialType, identifier, secret)
        cred.save()
        return cred

    @classmethod
    def deleteExpired(cls, credType):
        now = time.time()
        creds = Credential.query.filter_by(credentialType=credType).all()
        for c in creds:
            if float(c.secret) < now:
                c.rm()

    
    def __repr__(self, *args, **kwargs):
        return "Credential(user={0.user.email},credentialType={0.credentialType},secret={0.secret})".format(self)
