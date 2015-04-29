from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, BOOLEAN
import uuid

class User(db.Model, ModelUtils):
    __tablename__ = 'user'
    id = Column(String,primary_key=True)
    username = Column(String)
    active = Column(BOOLEAN)
    authenticated = Column(BOOLEAN)

    
    @classmethod
    def new(cls):
        user = cls()
        user.save()
        return user

    def __init__(self):
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
    
    
