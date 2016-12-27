
from flask_wtf.form import FlaskForm
from wtforms.fields.simple import TextField
from pdoauth.forms import credentialValidator, userNameValidator,\
    passwordValidator

class LoginForm(FlaskForm):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
    password = TextField('password', passwordValidator)
