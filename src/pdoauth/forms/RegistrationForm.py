from flask_wtf.form import Form
from wtforms import TextField, validators

class RegistrationForm(Form):
    credentialType = TextField('credentialType',[validators.AnyOf(values=['password'])])
    identifier = TextField('identifier', [validators.Length(min=4)])
    secret = TextField('secret', [validators.Length(min=8)])
    email = TextField('email', [validators.Email()])
    digest = TextField('digest')
    
    