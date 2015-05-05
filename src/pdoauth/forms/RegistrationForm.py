from flask_wtf.form import Form
from wtforms import TextField

class RegistrationForm(Form):
    credentialtype = TextField('password')
    identifier = TextField('identifier')
    secret = TextField('secret')
    email = TextField('email')
    digest = TextField('digest')

    def validate(self):
        return True
#FIXME: this is clearly wrong! Please see auth.py, main.py, MainTest.py and login.html for bits and pieces