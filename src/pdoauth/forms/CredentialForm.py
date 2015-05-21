from pdoauth.models.Credential import Credential
from wtforms.validators import ValidationError
from pdoauth.forms.LoginForm import LoginForm

class CredentialForm(LoginForm):
    def validate_identifier(self, field):
        if Credential.get(self.credentialType.data, self.identifier.data):
            raise ValidationError("There is already a user with that username")


    
    