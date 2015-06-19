from pdoauth.forms.CSRFForm import CSRFForm
from wtforms.fields.simple import TextField
from pdoauth.forms import secretValidator

class DeregisterDoitForm(CSRFForm):
    deregister_secret = TextField('deregister_secret', secretValidator)

