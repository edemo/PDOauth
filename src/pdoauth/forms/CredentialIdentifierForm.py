
from wtforms.fields.simple import TextField
from pdoauth.forms import credentialValidator, userNameValidator
from pdoauth.forms.CSRFForm import CSRFForm

class CredentialIdentifierForm(CSRFForm):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
