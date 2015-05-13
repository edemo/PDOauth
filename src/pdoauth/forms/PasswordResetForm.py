
from flask_wtf.form import Form
from wtforms import TextField, validators
    
class PasswordResetForm(Form):
    secret = TextField('secret', [validators.Length(min=36,max=36)])
    password = TextField('password', [validators.Length(min=8)])
