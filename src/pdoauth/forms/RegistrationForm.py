from flask_wtf.form import Form
from wtforms import TextField

class RegistrationForm(Form):
    credentialtype = TextField('password')
    identifier = TextField('identifier')
    secret = TextField('secret')
    email = TextField('email')
    digest = TextField('digest')
    
    