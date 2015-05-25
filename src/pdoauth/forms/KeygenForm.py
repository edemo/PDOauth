
from flask_wtf.form import Form
from wtforms.fields.simple import TextField, BooleanField
from pdoauth.forms import emailValidator, passwordValidator
    
class KeygenForm(Form):
    pubkey = TextField('pubkey', passwordValidator)
    email = TextField('email', emailValidator)
    createUser = BooleanField('createUser')
