from flask_wtf.form import Form
from wtforms import TextField
from pdoauth.forms import credentialValidator, userNameValidator,\
    passwordValidator, emailValidator, digestValidator

class RegistrationForm(Form):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
    secret = TextField('secret', passwordValidator)
    email = TextField('email', emailValidator)
    digest = TextField('digest', digestValidator)
    
    