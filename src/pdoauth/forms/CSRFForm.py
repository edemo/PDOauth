from flask_wtf.form import Form
from wtforms.fields.simple import TextField
from pdoauth.forms import csrfValidator

class CSRFForm(Form):
    csrf_token = TextField('csrf_token', validators = csrfValidator)

