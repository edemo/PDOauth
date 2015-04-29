from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.orm import relationship
from pdoauth.models.User import User

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
    def new(cls, user, credentialType, identifier, secret):
        cred = cls(user, credentialType, identifier, secret)
        cred.save()
        return cred
