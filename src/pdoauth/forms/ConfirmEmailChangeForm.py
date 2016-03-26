from flask_wtf.form import Form
from wtforms.fields.core import BooleanField
from pdoauth.forms import secretValidator
from wtforms.fields.simple import TextField

class ConfirmEmailChangeForm(Form):
    confirm = BooleanField('confirm')
    secret = TextField('secret', secretValidator)
