from wtforms import TextField
from pdoauth.forms import digestValidator, optional
from pdoauth.forms.CSRFForm import CSRFForm

class DigestUpdateForm(CSRFForm):
    digest = TextField('digest', optional(digestValidator))
