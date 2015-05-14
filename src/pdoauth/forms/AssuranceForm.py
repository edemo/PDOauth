
from wtforms import TextField
from pdoauth.forms.CSRFForm import CSRFForm
from pdoauth.forms import digestValidator, assuranceValidator, emailValidator


class AssuranceForm(CSRFForm):
    digest = TextField('digest', digestValidator)
    assurance = TextField('assurance', assuranceValidator)
    email = TextField('email', emailValidator)

