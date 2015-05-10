
from wtforms import TextField, validators
from pdoauth.forms.CSRFForm import CSRFForm


class AssuranceForm(CSRFForm):
    digest = TextField('digest', [validators.Length(min=4, max=50)])
    assurance = TextField('assurance', [validators.Length(min=4, max=50)])
    email = TextField('email', [validators.Length(min=8, max=50)])

