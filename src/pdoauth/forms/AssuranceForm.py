
from wtforms import TextField
from pdoauth.forms.CSRFForm import CSRFForm
from pdoauth.forms import digestValidator, assuranceValidator, emailValidator,\
    optional


class AssuranceForm(CSRFForm):
    digest = TextField('digest', optional(digestValidator))
    assurance = TextField('assurance', assuranceValidator)
    email = TextField('email', optional(emailValidator))

