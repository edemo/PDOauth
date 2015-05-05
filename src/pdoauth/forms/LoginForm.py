
from flask_wtf.form import Form
from wtforms import TextField, validators
    
class LoginForm(Form):
    username = TextField('username', [validators.Length(min=4, max=25)])
    password = TextField('password', [validators.Length(min=8)])
