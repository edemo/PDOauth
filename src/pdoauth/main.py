from pdoauth.app import app, login_manager, mail
from pdoauth.AuthProvider import AuthProvider
from pdoauth.Controller import Controller
from flask.helpers import send_from_directory
from pdoauth.models.User import User
import os
from flask.globals import request
from urllib import urlencode
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.Decorators import Decorators
from pdoauth.forms.KeygenForm import KeygenForm
from pdoauth.forms.DeregisterForm import DeregisterForm
from pdoauth.forms.PasswordChangeForm import PasswordChangeForm
from pdoauth.forms.DigestUpdateForm import DigestUpdateForm
from pdoauth.forms.PasswordResetForm import PasswordResetForm
from pdoauth.forms.RegistrationForm import RegistrationForm
from pdoauth.forms.AssuranceForm import AssuranceForm
from pdoauth.forms.CredentialForm import CredentialForm
from pdoauth.forms.CredentialIdentifierForm import CredentialIdentifierForm

controller = Controller.getInstance()
controller.mail = mail
controller.app = app
Decorators.app = app

def getStaticPath():
    mainpath = os.path.abspath(__file__)
    up = os.path.dirname
    ret = os.path.join(up(up(up(mainpath))), 'static')
    return ret

staticPath=getStaticPath()

@login_manager.unauthorized_handler
def unauthorized():
    resp = controller.error_response(["authentication needed"], 302)
    uri = "{1}?{0}".format(urlencode({"next": request.url}), app.config.get("START_URL"))
    resp.headers['Location'] = uri
    return resp

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@Decorators.interfaceFunc("/login", methods=["POST"], formClass= LoginForm, status=403)
def login(form):
    return controller.do_login(form)

@Decorators.interfaceFunc("/ssl_login", methods=["GET"])
def ssl_login():
    return controller.do_ssl_login()

@Decorators.interfaceFunc("/v1/oauth2/auth", methods=["GET"], checkLoginFunction=Decorators.checkLogin)
def authorization_code():
    "see http://tech.shift.com/post/39516330935/implementing-a-python-oauth-2-0-provider-part-1"
    return AuthProvider.auth_interface()

@Decorators.interfaceFunc("/keygen", methods=["POST"], formClass=KeygenForm)
def keygen(form):
    return controller.do_keygen(form)

@Decorators.interfaceFunc("/deregister", methods=["POST"], formClass=DeregisterForm)
def deregister(form):
    return controller.do_deregister(form)

@Decorators.interfaceFunc("/logout", methods=["GET"], checkLoginFunction=Decorators.checkLogin)
def logout():
    return controller.do_logout()

@Decorators.interfaceFunc("/v1/oauth2/token", methods=["POST"])
def token():
    return AuthProvider.token_interface()

@Decorators.interfaceFunc("/v1/users/<userid>", methods=["GET"],
    checkLoginFunction=Decorators.authenticateUserOrBearer)
def showUser(userid):
    return controller.do_show_user(userid)

@Decorators.interfaceFunc("/v1/users/me/change_password", methods=["POST"],
    formClass=PasswordChangeForm, checkLoginFunction=Decorators.checkLogin)
def changePassword(form):
    return controller.do_change_password(form)

@Decorators.interfaceFunc("/v1/users/<email>/passwordreset", methods=["GET"])
def sendPasswordResetEmail(email):
    return controller.do_send_password_reset_email(email)

@Decorators.interfaceFunc("/v1/users/me/update_hash", methods=["POST"],
    formClass=DigestUpdateForm, checkLoginFunction=Decorators.checkLogin)
def updateHash(form):
    return controller.do_update_hash(form)

@Decorators.interfaceFunc("/v1/password_reset", methods=["POST"],
    formClass=PasswordResetForm)
def passwordReset(form):
    return controller.do_password_reset(form)

@Decorators.interfaceFunc("/v1/register", methods=["POST"],
    formClass=RegistrationForm)
def register(form):
    return controller.do_registration(form)

@Decorators.interfaceFunc("/v1/verify_email/<token>", methods=["GET"])
def verifyEmail(token):
    return controller.do_verify_email(token)

@Decorators.interfaceFunc("/v1/user_by_email/<email>", methods=["GET"],
    checkLoginFunction=Decorators.checkLogin)
def get_by_email(email):
    return controller.do_get_by_email(email)

@Decorators.interfaceFunc("/v1/add_assurance", methods=["POST"],
    formClass=AssuranceForm, checkLoginFunction=Decorators.checkLogin)
def add_assurance(form):
    return controller.do_add_assurance(form)

@Decorators.interfaceFunc("/v1/add_credential", methods=["POST"],
    formClass=CredentialForm, checkLoginFunction=Decorators.checkLogin)
def add_credential(form):
    return controller.do_add_credential(form)

@Decorators.interfaceFunc("/v1/remove_credential", methods=["POST"],
    formClass=CredentialIdentifierForm, checkLoginFunction=Decorators.checkLogin)
def remove_credential(form):
    return controller.do_remove_credential(form)

@Decorators.interfaceFunc("/uris", methods=["GET"])
def uriservice():
    return controller.do_uris()

@Decorators.interfaceFunc("/static/<path:path>", methods=["GET"])
def send_static(path):
    return send_from_directory(staticPath, path)
