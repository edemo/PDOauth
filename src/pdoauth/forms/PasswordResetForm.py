
from flask_wtf.form import FlaskForm
from wtforms import TextField
from pdoauth.forms import passwordValidator, secretValidator
    
class PasswordResetForm(FlaskForm):
    secret = TextField('secret', secretValidator)
    password = TextField('password', passwordValidator)
