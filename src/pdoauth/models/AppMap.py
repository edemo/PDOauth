#pylint: disable=invalid-name, no-member, too-many-arguments
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.orm import relationship
from pdoauth.models.User import User
from pdoauth.models.Application import Application
from pdoauth.CryptoUtils import CryptoUtils

class AppMap(db.Model, ModelUtils, CryptoUtils):
    __tablename__ = 'app_map'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, foreign_keys=[user_id])
    app_id = Column(Integer, ForeignKey('application.id'))
    app = relationship(Application, foreign_keys=[app_id])
    email = Column(String)

    def __init__(self, app, user):
        self.app = app
        self.user = user
        self.email = "{0}@vala.hol".format(self.randomAsciiString(5))

    @classmethod
    def getEmailFor(cls, app, user):
        appMap = AppMap.query.filter_by(user=user, app=app).first()
        if appMap is None:
            appMap = AppMap(user=user, app=app)
            appMap.save()
        return appMap
