from pdoauth.app import db
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.orm import relationship
from pdoauth.models.User import User
import time
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.sql.functions import func

emailVerification = "emailverification"

class Assurance(db.Model, ModelUtils):
    __tablename__ = 'assurance'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    timestamp = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, foreign_keys=[user_id])
    assurer_id = Column(Integer, ForeignKey('user.id'))
    assurer = relationship(User, foreign_keys=[assurer_id])

    def __init__(self, user, name, assurer, timestamp):
        self.user = user
        self.name = name
        self.assurer = assurer
        self.timestamp = timestamp
        
    def as_dict(self):
        return dict(
            user=self.user.email,
            name = self.name,
            assurer = self.assurer.email,
            timestamp = self.timestamp,
            readable_time = time.asctime(time.gmtime(self.timestamp)))
        

    @classmethod
    def listByUser(cls, user, assurance=None):
        if assurance is not None:
            return Assurance.query.filter_by(user=user, name=assurance).all()
        assurances = Assurance.query.filter_by(user=user).all()
        return assurances

    @classmethod
    def getByUser(cls, user):
        assurances = cls.listByUser(user)
        r = {}
        for ass in assurances:
            if not ass.name in r:
                r[ass.name] = []
            r[ass.name].append(ass.as_dict())
        return r

    @classmethod
    def new(cls, user, name, assurer, timestamp = None):
        if timestamp is None:
            timestamp = time.time()
        assurance = cls(user, name, assurer, timestamp)
        assurance.save()
        return assurance
    
    def __repr__(self):
        return "Assurance({0},{1},{2},{3})".format(self.user, self.name, self.assurer, self.timestamp)

    @classmethod
    def removeAllForUser(cls, user):
        instances = cls.query.filter_by(user=user).all()
        for instance in instances:
            instance.rm()
            
    @classmethod
    def getStats(klass):
        assuranceStats = dict()
        assurances = klass.query.with_entities(Assurance.name).add_column(func.count(klass.name)).group_by(klass.name).all()
        for name, value in assurances:
            assuranceStats[name] = value
        
        return assuranceStats



User.subscribe(Assurance.removeAllForUser, "pre_rm")