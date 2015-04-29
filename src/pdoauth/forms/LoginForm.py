
from flask_wtf.form import Form
from wtforms import TextField
    
class LoginForm(Form):
    username = TextField('username')
    password = TextField('password')
