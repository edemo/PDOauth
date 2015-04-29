import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging

logging.basicConfig()
login_manager = LoginManager()
app = flask.Flask(__name__)
app.config.from_object("config.Config")
login_manager.init_app(app)
db = SQLAlchemy(app)
session = db.session

