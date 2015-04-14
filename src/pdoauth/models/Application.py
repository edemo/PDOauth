from sqlalchemy import Column, Integer, String
from pdoauth.app import db

class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String)
