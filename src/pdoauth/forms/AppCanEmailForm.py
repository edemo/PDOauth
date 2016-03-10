from wtforms import TextField, BooleanField
from pdoauth.forms import userNameValidator
from pdoauth.forms.CSRFForm import CSRFForm

class AppCanEmailForm(CSRFForm):
    appname = TextField('appname', userNameValidator)
    canemail = BooleanField('canemail')
