from flask_wtf.form import Form
from flask.globals import session
from wtforms.validators import ValidationError
from wtforms.fields.simple import TextField

def csrf_check(self, field):
    sessionid = session['csrf_token']
    if not sessionid == field.data:
        raise ValidationError('csrf validation error')


class CSRFForm(Form):
    csrf_token = TextField('csrf_token', validators = [csrf_check])

