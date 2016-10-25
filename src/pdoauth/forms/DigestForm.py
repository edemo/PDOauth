from wtforms import TextField
from pdoauth.forms import digestValidator, optional
from flask_wtf.form import FlaskForm

class DigestForm(FlaskForm):
    digest = TextField('digest', optional(digestValidator))
