
from flask_wtf.form import Form
from wtforms.fields.simple import TextField
from pdoauth.forms import credentialValidator, userNameValidator,\
    passwordValidator

class LoginForm(Form):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
    secret = TextField('secret', passwordValidator)
