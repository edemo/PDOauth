
from flask_wtf.form import Form
from wtforms import TextField
from pdoauth.forms import passwordValidator
    
class PasswordResetForm(Form):
    secret = TextField('secret', passwordValidator)
    password = TextField('password', passwordValidator)
