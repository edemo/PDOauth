from wtforms import TextField
from pdoauth.forms import emailValidator, digestValidator, optional
from pdoauth.models.User import User
from wtforms.validators import ValidationError
from pdoauth.forms.CredentialForm import CredentialForm

class RegistrationForm(CredentialForm):
    email = TextField('email', emailValidator)
    digest = TextField('digest', optional(digestValidator))
    
    def validate_email(self,field):
        if User.getByEmail(field.data):
            raise ValidationError("There is already a user with that email")
