from wtforms import validators
from flask.globals import session
from wtforms.validators import ValidationError

def csrfCheck(self, field):
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')

credentialTypes = ['password', 'facebook']
credentialValidator = [validators.AnyOf(values=credentialTypes)]
userNameValidator = [validators.Length(min=4, max=25)]
passwordValidator = [validators.Length(min=8)]
emailValidator = [validators.Email()]
digestValidator = [validators.Optional(), validators.Length(min=4, max=50)]
assuranceValidator = [validators.Length(min=4, max=50)]
csrfValidator = [csrfCheck]
