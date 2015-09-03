#pylint: disable=invalid-name, no-member, too-many-arguments
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from pdoauth.app import db
from pdoauth.app import app as theApplication
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.orm import relationship
from pdoauth.models.User import User
from pdoauth.models.Application import Application
from pdoauth.CryptoUtils import CryptoUtils
from Crypto.Hash.SHA512 import SHA512Hash

class AppMap(db.Model, ModelUtils, CryptoUtils):
    __tablename__ = 'app_map'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, foreign_keys=[user_id])
    app_id = Column(Integer, ForeignKey('application.id'))
    app = relationship(Application, foreign_keys=[app_id])
    userid = Column(String)

    def __init__(self, app, user):
        self.app = app
        self.user = user
        self.userid = SHA512Hash(app.appid + user.userid).hexdigest()[:16]

    def getEmail(self):
        return "{0}.{1}@{2}".format(
                        self.userid,
                        self.app.name,
                        theApplication.config.get('EMAIL_DOMAIN'))
    @classmethod
    def get(cls, app, user):
        appMapEntry = AppMap.query.filter_by(app=app, user=user).first()
        if appMapEntry is None:
            appMapEntry = AppMap(app,user)
            appMapEntry.save()
        return appMapEntry
