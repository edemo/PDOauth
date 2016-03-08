#pylint: disable=unused-argument, invalid-name
from wtforms import validators
from flask.globals import session
from wtforms.validators import ValidationError
import pdoauth.I18n

credentialTypes = ['password', 'facebook', 'certificate']

passwordShouldContainLowercase = _("password should contain lowercase")
passwordShouldContainUppercase = _("password should contain uppercase")
passwordShouldContainDigit = _("password should contain digit")
secretShouldContainLowercase = _("secret should contain lowercase")
secretShouldContainDigit = _("secret should contain digit")
credErrString = _("credentialType: Invalid value, must be one of:")
credErr = '"{0} {1}."'.format(credErrString, ", ".join(credentialTypes))

def csrfCheck(self, field):
    if not session.has_key('csrf_token'):
        raise ValidationError('csrf validation error')
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')

def optional(validator):
    return [validators.Optional()] + validator


credentialValidator = [validators.AnyOf(values=credentialTypes)]
userNameValidator = [validators.Length(min=4, max=250)]
passwordValidator = [validators.Length(min=8),
                     validators.Regexp(".*[a-z].*", message=passwordShouldContainLowercase),
                     validators.Regexp(".*[A-Z].*", message=passwordShouldContainUppercase),
                     validators.Regexp(".*[0-9].*", message=passwordShouldContainDigit)]
secretValidator = [validators.Length(min=8),
                     validators.Regexp(".*[a-z].*", message=secretShouldContainLowercase),
                     validators.Regexp(".*[0-9].*", message=secretShouldContainDigit)]
emailValidator = [validators.Email()]
digestValidator = [validators.Length(min=128, max=128), validators.regexp("[0-9A-Fa-f]*")]
assuranceValidator = [validators.Length(min=4, max=50)]
csrfValidator = [csrfCheck]
