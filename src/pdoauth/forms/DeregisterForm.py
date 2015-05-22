from pdoauth.forms.LoginForm import LoginForm
from pdoauth.forms.CSRFForm import CSRFForm

    
class DeregisterForm(LoginForm, CSRFForm):
    pass
