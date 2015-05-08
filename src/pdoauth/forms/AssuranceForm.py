
from flask_wtf.form import Form
from wtforms import TextField, validators
from flask.globals import session
from wtforms.validators import ValidationError

def csrf_check(form, field):
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')

class AssuranceForm(Form):
    digest = TextField('digest', [validators.Length(min=4, max=50)])
    assurance = TextField('assurance', [validators.Length(min=4, max=50)])
    email = TextField('email', [validators.Length(min=8, max=50)])
    csrf_token = TextField('csrf_token', validators = [csrf_check])

