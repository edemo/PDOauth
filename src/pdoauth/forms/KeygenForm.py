
from wtforms.fields.simple import TextField, BooleanField
from pdoauth.forms import emailValidator, passwordValidator
from pdoauth.forms.DigestForm import DigestForm
    
class KeygenForm(DigestForm):
    pubkey = TextField('pubkey', passwordValidator)
    email = TextField('email', emailValidator)
    createUser = BooleanField('createUser')
