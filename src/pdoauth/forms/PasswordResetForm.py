
from flask_wtf.form import Form
from wtforms import TextField
from pdoauth.forms import passwordValidator, secretValidator
    
class PasswordResetForm(Form):
    secret = TextField('secret', secretValidator)
    password = TextField('password', passwordValidator)
