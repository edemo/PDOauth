
from wtforms import TextField, validators
from pdoauth.forms.CSRFForm import CSRFForm


class PasswordChangeForm(CSRFForm):
    oldPassword = TextField('oldPassword', [validators.Length(min=4, max=50)])
    newPassword = TextField('newPassword', [validators.Length(min=4, max=50)])

