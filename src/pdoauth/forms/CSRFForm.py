from flask_wtf import FlaskForm
from wtforms.fields.simple import TextField
from pdoauth.forms import csrfValidator

class CSRFForm(FlaskForm):
    csrf_token = TextField('csrf_token', validators = csrfValidator)

