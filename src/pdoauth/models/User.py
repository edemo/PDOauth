from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, BOOLEAN
import uuid

class User(db.Model, ModelUtils):
    __tablename__ = 'user'
    id = Column(String,primary_key=True)
    username = Column(String)
    email = Column(String)
    hash = Column(String)
    active = Column(BOOLEAN)
    authenticated = Column(BOOLEAN)

    
    @classmethod
    def new(cls, name=None, email=None, digest=None):
        user = cls(name, email,digest)
        user.save()
        return user

    def __init__(self, name=None, email=None, digest=None):
        if name is not None:
            self.username = name
        if email is not None:
            self.email = email
        if digest is not None:
            self.hash = digest

        self.id=unicode(uuid.uuid4())
        self.active = False
        self.authenticated = False

    def get_id(self):
        return self.id
    
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

    @classmethod
    def get(cls, userid):
        return User.query.filter_by(id=userid).first()
    
    
