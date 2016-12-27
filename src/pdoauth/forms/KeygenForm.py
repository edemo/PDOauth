
from wtforms.fields.simple import TextField, BooleanField
from pdoauth.forms import emailValidator, secretValidator
from pdoauth.forms.DigestForm import DigestForm
    
class KeygenForm(DigestForm):
    pubkey = TextField('pubkey', secretValidator)
    email = TextField('email', emailValidator)
    createUser = BooleanField('createUser')
