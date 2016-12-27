from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.orm import relationship
from pdoauth.models.User import User
import time
from pdoauth.ReportedError import ReportedError


class AlreadyExistingCredential(Exception):
    pass


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
    
    def getAdditionalInfo(self):
        l = self.identifier.split(":")
        if len(l)>1:
            return l[1]
        return None

    @classmethod
    def get(cls, credentialType, identifier):
        return Credential.query.filter_by(credentialType = credentialType, identifier = identifier).first()

    @classmethod
    def getBySecret(cls, credentialType, secret):
        return Credential.query.filter_by(credentialType = credentialType, secret = secret).first()

    @classmethod
    def getByUser(cls, user, credentialType=None):
        if credentialType is None:
            return Credential.query.filter_by(user=user).all()
        return Credential.query.filter_by(user=user, credentialType=credentialType).first()
    
    @classmethod
    def new(cls, user, credentialType, identifier, secret):
        oldcred = cls.get(credentialType, identifier)
        if oldcred is not None:
            raise ReportedError('Already existing credential', 400)
        cred = cls(user, credentialType, identifier, secret)
        cred.save()
        return cred

    def getExpirationTime(self):
        credTime = float(self.identifier.split(':')[0])
        return credTime

    @classmethod
    def deleteExpired(cls, credType):
        now = time.time()
        creds = Credential.query.filter_by(credentialType=credType).all()
        for c in creds:
            if c.getExpirationTime() < now:
                c.rm()

    def __repr__(self, *args, **kwargs):
        return "Credential(user={0.user.email},credentialType={0.credentialType},identifier={0.identifier},secret={0.secret})".format(self)


    @classmethod
    def getByUser_as_dictlist(cls, user):
        l = []
        creds = Credential.query.filter_by(user=user).all()
        for cred in creds:
            l.append(dict(
                credentialType = cred.credentialType,
                identifier = cred.identifier
            ))
        return l

    @classmethod
    def removeAllForUser(cls, user):
        creds = Credential.query.filter_by(user=user).all()
        for cred in creds:
            cred.rm()

User.subscribe(Credential.removeAllForUser, "pre_rm")

