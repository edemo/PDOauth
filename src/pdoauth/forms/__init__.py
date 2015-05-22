from wtforms import validators
from flask.globals import session
from wtforms.validators import ValidationError

def csrfCheck(self, field):
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')

def formValidated(formClass, status=400):
    def decorator(func):
        def validated(self):
            form = formClass()
            if self.validate_on_submit(form):
                return func(self, form)
            return self.form_validation_error_response(form, status)
        return validated
    return decorator

def optional(validator):
    return [validators.Optional()] + validator
credentialTypes = ['password', 'facebook']
credentialValidator = [validators.AnyOf(values=credentialTypes)]
userNameValidator = [validators.Length(min=4, max=25)]
passwordValidator = [validators.Length(min=8),
                     validators.Regexp(".*[a-z].*", message="password should contain lowercase"),
                     validators.Regexp(".*[A-Z].*", message="password should contain uppercase"),
                     validators.Regexp(".*[0-9].*", message="password should contain digit")]
secretValidator = [validators.Length(min=8),
                     validators.Regexp(".*[a-z].*", message="password should contain lowercase"),
                     validators.Regexp(".*[0-9].*", message="password should contain digit")]
emailValidator = [validators.Email()]
digestValidator = [validators.Length(min=256, max=256), validators.regexp("[0-9A-Fa-f]*")]
assuranceValidator = [validators.Length(min=4, max=50)]
csrfValidator = [csrfCheck]
