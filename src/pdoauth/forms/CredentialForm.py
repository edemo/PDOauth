from pdoauth.models.Credential import Credential
from wtforms.validators import ValidationError
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.Messages import thereIsAlreadyAUserWithThatUsername

class CredentialForm(LoginForm):
    def validate_identifier(self, field):
        if Credential.get(self.credentialType.data, self.identifier.data):
            raise ValidationError(thereIsAlreadyAUserWithThatUsername)


    
    