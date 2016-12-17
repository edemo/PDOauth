from pdoauth.app import app, login_manager, mail
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
from pdoauth.forms.EmailChangeForm import EmailChangeForm
from pdoauth.forms.ConfirmEmailChangeForm import ConfirmEmailChangeForm
from pdoauth.forms.CredentialForm import CredentialForm
from pdoauth.forms.CredentialIdentifierForm import CredentialIdentifierForm
from pdoauth.forms.DeregisterDoitForm import DeregisterDoitForm
from pdoauth.FlaskInterface import FlaskInterface
from pdoauth.forms.TokenInterfaceForm import TokenInterfaceForm
from pdoauth.AppHandler import AppHandler
from pdoauth.forms.AppCanEmailForm import AppCanEmailForm

webInterface = FlaskInterface() # pylint: disable=invalid-name
CONTROLLER = Controller(webInterface)
CONTROLLER.mail = mail
CONTROLLER.app = app
DECORATOR = Decorators(app, webInterface)
AUTHPROVIDER = AuthProvider(webInterface)
APPHANDLER = AppHandler(webInterface)

def getStaticPath():
    staticDirectory = os.path.join(os.path.dirname(__file__),"..", "..", "static")
    return os.path.abspath(staticDirectory)

STATIC_PATH=getStaticPath()

@login_manager.user_loader
def getUser(userid):
    return User.get(userid)

@DECORATOR.interfaceFunc("/v1/login", methods=["POST"], formClass= LoginForm, status=403)
def login(form):
    return CONTROLLER.doLogin(form)

@DECORATOR.interfaceFunc("/v1/ssl_login", methods=["GET"])
def ssl_login():
    return CONTROLLER.doSslLogin()

@DECORATOR.interfaceFunc("/v1/oauth2/auth", methods=["GET"], checkLoginFunction=CONTROLLER.redirectIfNotLoggedIn)
def authorization_code():
    "see http://tech.shift.com/post/39516330935/implementing-a-python-oauth-2-0-provider-part-1"
    return AUTHPROVIDER.auth_interface()

@DECORATOR.interfaceFunc("/v1/ca/signreq", methods=["POST"], formClass=KeygenForm)
def signreq(form):
    return CONTROLLER.signRequest(form)

@DECORATOR.interfaceFunc("/v1/deregister", methods=["POST"], formClass=DeregisterForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def deregister(form):
    return CONTROLLER.doDeregister(form)

@DECORATOR.interfaceFunc("/v1/deregister_doit", methods=["POST"], formClass=DeregisterDoitForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def deregister_doit(form):
    return CONTROLLER.doDeregistrationDoit(form)

@DECORATOR.interfaceFunc("/v1/logout", methods=["GET"], checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def logout():
    return CONTROLLER.doLogout()

@DECORATOR.interfaceFunc("/v1/oauth2/token", methods=["POST"], formClass=TokenInterfaceForm)
def token(form):
    return AUTHPROVIDER.token_interface(form)

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

@DECORATOR.interfaceFunc("/v1/send_verify_email", methods=["GET"], checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def sendVerifyEmail():
    return CONTROLLER.sendVerifyEmail()

@DECORATOR.interfaceFunc("/v1/user_by_email/<email>", methods=["GET"],
    checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def get_by_email(email):
    return CONTROLLER.doGetByEmail(email)

@DECORATOR.interfaceFunc("/v1/emailchange", methods=["POST"],
    formClass=EmailChangeForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def email_change(form):
    return CONTROLLER.changeEmail(form)

@DECORATOR.interfaceFunc("/v1/confirmemailchange", methods=["POST"],
    formClass=ConfirmEmailChangeForm)
def confirm_email_change(form):
    return CONTROLLER.confirmEmailChange(form)

@DECORATOR.interfaceFunc("/v1/add_assurance", methods=["POST"],
    formClass=AssuranceForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def add_assurance(form):
    return CONTROLLER.doAddAssurance(form)

@DECORATOR.interfaceFunc("/v1/add_credential", methods=["POST"],
    formClass=CredentialForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def add_credential(form):
    return CONTROLLER.doAddCredential(form)

@DECORATOR.interfaceFunc("/v1/getmyapps", methods=["GET"], checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def get_my_apps():
    return APPHANDLER.getApplistInterFace()

@DECORATOR.interfaceFunc("/v1/setappcanemail", methods=["POST"], checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn,
    formClass = AppCanEmailForm)
def set_app_can_email(form):
    return APPHANDLER.setAppCanEmail(form)

@DECORATOR.interfaceFunc("/v1/remove_credential", methods=["POST"],
    formClass=CredentialIdentifierForm, checkLoginFunction=CONTROLLER.jsonErrorIfNotLoggedIn)
def remove_credential(form):
    return CONTROLLER.doRemoveCredential(form)

@DECORATOR.interfaceFunc("/v1/uris", methods=["GET"])
def uriservice():
    return CONTROLLER.doUris()

@DECORATOR.interfaceFunc("/v1/statistics", methods=["GET"])
def statisticsService():
    return CONTROLLER.getStatsAsJson()

@DECORATOR.interfaceFunc("/static/<path:path>", methods=["GET"])
def send_static(path):
    return send_from_directory(STATIC_PATH, path)
