#pylint: disable=invalid-name, no-member, too-many-arguments
from sqlalchemy.sql.schema import Column, ForeignKey
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils
from sqlalchemy.orm import relationship
from pdoauth.models.Application import Application
from pdoauth.CryptoUtils import CryptoUtils
from sqlalchemy.sql.sqltypes import Integer, String

class AppAssurance(db.Model, ModelUtils, CryptoUtils):
    __tablename__ = 'app_assurance'
    id = Column(Integer,primary_key=True)
    assurance = Column(String)
    app_id = Column(Integer, ForeignKey('application.id'))
    app = relationship(Application, foreign_keys=[app_id])

    def __init__(self, app, name):
        self.app = app
        self.assurance = name

    @classmethod
    def get(cls, app):
        assurances = AppAssurance.query.filter_by(app=app).all()
        assuranceList = []
        for item in assurances:
            assuranceList.append(item.assurance)
        return assuranceList

    @classmethod
    def add(cls, app, name):
        if name in cls.get(app):
            return None
        appAssurance = AppAssurance(app,name)
        appAssurance.save()
        return appAssurance


    
    @classmethod
    def removeAllForApp(cls, app):
        applications = cls.query.filter_by(app=app).all()
        for application in applications:
            application.rm()

Application.subscribe(AppAssurance.removeAllForApp, "pre_rm")
