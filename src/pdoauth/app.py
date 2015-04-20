import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
session = db.session

