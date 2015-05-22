from wtforms import TextField
from pdoauth.forms import emailValidator
from pdoauth.models.User import User
from wtforms.validators import ValidationError
from pdoauth.forms.CredentialForm import CredentialForm
from pdoauth.forms.DigestForm import DigestForm

class RegistrationForm(CredentialForm, DigestForm):
    email = TextField('email', emailValidator)

    def validate_email(self,field):
        if User.getByEmail(field.data):
            raise ValidationError("There is already a user with that email")
