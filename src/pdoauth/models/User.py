from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, BOOLEAN, Integer
import uuid


class AlreadyExistingUser(Exception):
    pass


class User(db.Model, ModelUtils):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    userid = Column(String, nullable = False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hash = Column(String)
    active = Column(BOOLEAN)
    authenticated = Column(BOOLEAN)

    @classmethod
    def getByEmail(cls, email):
        u= cls.query.filter_by(email=email).first()
        return u

    @classmethod
    def new(cls, email, digest=None):
        u = cls.getByEmail(email)
        if u is not None:
            raise AlreadyExistingUser()
        user = cls( email,digest)
        user.save()
        return user

    def __init__(self, email, digest=None):
        self.email = email
        if digest is not None:
            self.hash = digest

        self.userid=unicode(uuid.uuid4())
        self.active = False
        self.authenticated = False

    def get_id(self):
        return self.userid
    
    def activate(self):
        self.active = True
        self.save()
        
    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated
    
    def set_authenticated(self):
        self.authenticated = True
        self.save()

    def is_anonymous(self):
        return False
    
    @classmethod
    def get(cls, userid):
        return User.query.filter_by(userid=userid).first()

    
    @classmethod
    def getByDigest(cls, digest):
        if digest == '' or digest is None:
            raise ValueError()
        return cls.query.filter_by(hash=digest).all()
