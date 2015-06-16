from pdoauth.app import app, login_manager, mail, db
from pdoauth.AuthProvider import AuthProvider
from pdoauth.Controller import Controller
from flask.helpers import send_from_directory
from pdoauth.models.User import User
import os
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
from pdoauth.forms.DeregisterDoitForm import DeregisterDoitForm
from pdoauth.FlaskInterface import FlaskInterface
from pdoauth import models  # @UnusedWildImport

db.create_all()

webInterface = FlaskInterface()
CONTROLLER = Controller(webInterface)
CONTROLLER.mail = mail
CONTROLLER.app = app
DECORATOR = Decorators(app, webInterface)
AUTHPROVIDER = AuthProvider(webInterface)

def getStaticPath():
    staticDirectory = os.path.join(os.path.dirname(__file__),"..", "..", "static")
    return os.path.abspath(staticDirectory)

STATIC_PATH=getStaticPath()

@login_manager.user_loader
def getUser(userid):
    return User.get(userid)

@DECORATOR.interfaceFunc("/login", methods=["POST"], formClass= LoginForm, status=403)
def login(form):
    return CONTROLLER.doLogin(form)

@DECORATOR.interfaceFunc("/ssl_login", methods=["GET"])
def ssl_login():
    return CONTROLLER.doSslLogin()

@DECORATOR.interfaceFunc("/v1/oauth2/auth", methods=["GET"], checkLoginFunction=CONTROLLER.redirectIfNotLoggedIn)
def authorization_code():
    "see http://tech.shift.com/post/39516330935/implementing-a-python-oauth-2-0-provider-part-1"
    return AUTHPROVIDER.auth_interface()

@DECORATOR.interfaceFunc("/keygen", methods=["POST"], formClass=KeygenForm)
def keygen(form):
    return CONTROLLER.doKeygen(form)

@DECORATOR.interfaceFunc("/deregister", methods=["POST"], formClass=DeregisterForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def deregister(form):
    return CONTROLLER.doDeregister(form)

@DECORATOR.interfaceFunc("/deregister_doit", methods=["POST"], formClass=DeregisterDoitForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def deregister_doit(form):
    return CONTROLLER.doDeregistrationDot(form)

@DECORATOR.interfaceFunc("/logout", methods=["GET"], checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def logout():
    return CONTROLLER.doLogout()

@DECORATOR.interfaceFunc("/v1/oauth2/token", methods=["POST"])
def token():
    return AUTHPROVIDER.token_interface()

@DECORATOR.interfaceFunc("/v1/users/<userid>", methods=["GET"],
    checkLoginFunction=CONTROLLER.authenticateUserOrBearer)
def showUser(userid):
    return CONTROLLER.doShowUser(userid)

@DECORATOR.interfaceFunc("/v1/users/me/change_password", methods=["POST"],
    formClass=PasswordChangeForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def changePassword(form):
    return CONTROLLER.doChangePassword(form)

@DECORATOR.interfaceFunc("/v1/users/<email>/passwordreset", methods=["GET"])
def sendPasswordResetEmail(email):
    return CONTROLLER.doSendPasswordResetEmail(email)

@DECORATOR.interfaceFunc("/v1/users/me/update_hash", methods=["POST"],
    formClass=DigestUpdateForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def updateHash(form):
    return CONTROLLER.doUpdateHash(form)

@DECORATOR.interfaceFunc("/v1/password_reset", methods=["POST"],
    formClass=PasswordResetForm)
def passwordReset(form):
    return CONTROLLER.doPasswordReset(form)

@DECORATOR.interfaceFunc("/v1/register", methods=["POST"],
    formClass=RegistrationForm)
def register(form):
    return CONTROLLER.doRegistration(form)

@DECORATOR.interfaceFunc("/v1/verify_email/<emailToken>", methods=["GET"])
def verifyEmail(emailToken):
    return CONTROLLER.doverifyEmail(emailToken)

@DECORATOR.interfaceFunc("/v1/user_by_email/<email>", methods=["GET"],
    checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def get_by_email(email):
    return CONTROLLER.doGetByEmail(email)

@DECORATOR.interfaceFunc("/v1/add_assurance", methods=["POST"],
    formClass=AssuranceForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def add_assurance(form):
    return CONTROLLER.doAddAssurance(form)

@DECORATOR.interfaceFunc("/v1/add_credential", methods=["POST"],
    formClass=CredentialForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def add_credential(form):
    return CONTROLLER.doAddCredential(form)

@DECORATOR.interfaceFunc("/v1/remove_credential", methods=["POST"],
    formClass=CredentialIdentifierForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def remove_credential(form):
    return CONTROLLER.doRemoveCredential(form)

@DECORATOR.interfaceFunc("/uris", methods=["GET"])
def uriservice():
    return CONTROLLER.doUris()

@DECORATOR.interfaceFunc("/static/<path:path>", methods=["GET"])
def send_static(path):
    return send_from_directory(STATIC_PATH, path)
