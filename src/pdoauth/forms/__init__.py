#pylint: disable=unused-argument, invalid-name
from wtforms import validators
from flask.globals import session
from wtforms.validators import ValidationError
from pdoauth.Messages import credErrString, passwordShouldContainLowercase, passwordShouldContainUppercase,\
    passwordShouldContainDigit, secretShouldContainLowercase,\
    secretShouldContainDigit, credentialTypeString

credentialTypes = ['password', 'facebook', 'certificate']

credErr = '"{0}: {1}: {2}."'.format(credentialTypeString,credErrString, ", ".join(credentialTypes))

def csrfCheck(self, field):
    if 'csrf_token' not in session:
        raise ValidationError('csrf validation error')
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')

def optional(validator):
    return [validators.Optional(strip_whitespace=False)] + validator


credentialValidator = [validators.AnyOf(values=credentialTypes)]
userNameValidator = [validators.Length(min=4, max=250)]
passwordValidator = [validators.Length(min=8),
                     validators.Regexp(".*[a-z].*", message=passwordShouldContainLowercase),
                     validators.Regexp(".*[A-Z].*", message=passwordShouldContainUppercase),
                     validators.Regexp(".*[0-9].*", message=passwordShouldContainDigit)]
secretValidator = [validators.Length(min=8),
                     validators.Regexp("(?s).*[a-z].*", message=secretShouldContainLowercase),
                     validators.Regexp("(?s).*[0-9].*", message=secretShouldContainDigit)]
emailValidator = [validators.Email()]
digestValidator = [validators.Length(min=128, max=128), validators.regexp("[0-9A-Fa-f]*")]
assuranceValidator = [validators.Length(min=4, max=50)]
csrfValidator = [csrfCheck]
