from flask_wtf.form import FlaskForm
from wtforms.fields.core import BooleanField
from pdoauth.forms import secretValidator
from wtforms.fields.simple import TextField

class ConfirmEmailChangeForm(FlaskForm):
    confirm = BooleanField('confirm')
    secret = TextField('secret', secretValidator)
