
from flask_wtf.form import Form
from wtforms import TextField, validators
    
class AssuranceForm(Form):
    digest = TextField('digest', [validators.Length(min=4, max=50)])
    assurance = TextField('assurance', [validators.Length(min=4, max=50)])
    email = TextField('email', [validators.Length(min=8, max=50)])
