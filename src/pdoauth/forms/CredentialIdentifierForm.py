
from flask_wtf.form import Form
from wtforms.fields.simple import TextField
from pdoauth.forms import credentialValidator, userNameValidator
    
class CredentialIdentifierForm(Form):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
