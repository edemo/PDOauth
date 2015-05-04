import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging
from flask_mail import Mail

logging.basicConfig()
login_manager = LoginManager()
app = flask.Flask(__name__)
app.config.from_object("config.Config")
mail = Mail(app)
login_manager.init_app(app)
db = SQLAlchemy(app)
session = db.session

