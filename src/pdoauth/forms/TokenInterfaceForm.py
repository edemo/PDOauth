from flask_wtf.form import Form
from wtforms.fields.simple import TextField

class TokenInterfaceForm(Form):
    grant_type = TextField('grant_type', [])
    client_id = TextField('client_id', [])
    client_secret = TextField('client_secret', [])
    redirect_uri = TextField('redirect_uri', [])
    scope = TextField('scope', [])
    code = TextField('code', [])

