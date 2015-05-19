from flask_wtf.form import Form
from wtforms import TextField
from pdoauth.forms import credentialValidator, userNameValidator,\
    passwordValidator, emailValidator, digestValidator, optional
from pdoauth.models.User import User
from wtforms.validators import ValidationError
from pdoauth.models.Credential import Credential

class RegistrationForm(Form):
    credentialType = TextField('credentialType',credentialValidator)
    identifier = TextField('identifier', userNameValidator)
    secret = TextField('secret', passwordValidator)
    email = TextField('email', emailValidator)
    digest = TextField('digest', optional(digestValidator))
    
    def validate_email(self,field):
        if User.getByEmail(field.data):
            raise ValidationError("There is already a user with that email")
        
    def validate_identifier(self, field):
        if Credential.get(self.credentialType.data, self.identifier.data):
            raise ValidationError("There is already a user with that username")


    
    