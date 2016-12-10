import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import SysLogHandler

handler = SysLogHandler(address='/dev/log')
login_manager = LoginManager()
app = flask.Flask(__name__, static_url_path='')
app.config.from_object("config.Config")
app.logger.addHandler(handler)
app.logger.info("logging started")
app.logger.setLevel(app.config.get("LOGLEVEL"))
mail = Mail(app)
login_manager.init_app(app)
db = SQLAlchemy(app)
session = db.session
