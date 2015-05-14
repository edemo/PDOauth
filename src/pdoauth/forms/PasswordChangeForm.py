
from wtforms import TextField
from pdoauth.forms.CSRFForm import CSRFForm
from pdoauth.forms import passwordValidator


class PasswordChangeForm(CSRFForm):
    oldPassword = TextField('oldPassword', passwordValidator)
    newPassword = TextField('newPassword', passwordValidator)

