from wtforms import TextField
from pdoauth.forms import digestValidator, optional
from flask_wtf.form import Form

class DigestForm(Form):
    digest = TextField('digest', optional(digestValidator))
