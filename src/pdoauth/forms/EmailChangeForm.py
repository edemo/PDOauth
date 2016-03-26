from pdoauth.forms.CSRFForm import CSRFForm
from pdoauth.forms import emailValidator
from wtforms.fields.simple import TextField

class EmailChangeForm(CSRFForm):
    newemail = TextField('newemail', emailValidator)
