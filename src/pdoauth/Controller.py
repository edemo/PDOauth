from pdoauth.app import mail, app
import flask
from pdoauth.models.User import User
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user, current_user, logout_user
from flask.globals import request, session
from pdoauth.forms.RegistrationForm import RegistrationForm
from pdoauth.models.Credential import Credential
from uuid import uuid4
import time
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.Assurance import Assurance, emailVerification
from pdoauth.forms.AssuranceForm import AssuranceForm
from flask import json
from pdoauth.forms.PasswordChangeForm import PasswordChangeForm
from pdoauth.forms.PasswordResetForm import PasswordResetForm
from pdoauth.forms import formValidated
from pdoauth.forms.CredentialForm import CredentialForm
from pdoauth.forms.DigestUpdateForm import DigestUpdateForm
from pdoauth.forms.CredentialIdentifierForm import CredentialIdentifierForm
from pdoauth.forms.DeregisterForm import DeregisterForm
from OpenSSL import crypto
import urlparse
from pdoauth.forms.KeygenForm import KeygenForm
from pyspkac.spkac import SPKAC
from M2Crypto import EVP, X509
from pdoauth.FlaskInterface import Responses, ReportedError, FlaskInterface

anotherUserUsingYourHash = "another user is using your hash"

class Controller(Responses):
    
    def __init__(self, interface):
        class __patched(self.__class__):
            pass
        __patched.__bases__ += (interface,)
        self.__class__ = __patched
    
    def email_verification(self, user):
        secret=unicode(uuid4())
        expiry = time.time() + 60*60*24*4
        Credential.new(user, 'emailcheck', unicode(expiry), secret )
        timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
        uri = "{0}/v1/verify_email/{1}".format(app.config.get('BASE_URL'),secret)
        text = """Hi, click on <a href="{0}">{0}</a> until {1} to verify your email""".format(uri, timeText)
        mail.send_message(subject="verification", body=text, recipients=[user.email], sender=app.config.get('SERVER_EMAIL_ADDRESS'))
    
    def isAllowedToGetUser(self, userid):
        allowed = False
        authuser = None
        authHeader = request.headers.get('Authorization')
        if current_user.is_authenticated():
            if userid == 'me':
                return (True,current_user)
            if Assurance.getByUser(current_user).has_key('assurer'):
                authuser = User.get(userid)
                return (True, authuser)
        if authHeader:
            token = authHeader.split(" ")[1]
            data = TokenInfoByAccessKey.find(token)
            targetuserid = data.tokeninfo.user_id
            authuser = User.get(targetuserid)
            allowed = authuser.id == userid or userid == 'me'
        return allowed, authuser
    

    def loginUser(self, user):
        user.set_authenticated()
        r = login_user(user)
        return r

    def returnUserAndLoginCookie(self, user):
        resp = self.as_dict(user)
        token = unicode(uuid4())
        session['csrf_token'] = token
        resp.set_cookie("csrf", token)
        return resp

    def finishLogin(self, user):
        r = self.loginUser(user)
        if r:
            return self.returnUserAndLoginCookie(user)
        raise ReportedError(["Inactive or disabled user"], status=403)

    def passwordLogin(self, form):
        user = CredentialManager.validate_from_form(form)
        if user is None:
            raise ReportedError(["Bad username or password"], status=403)
        return self.finishLogin(user)

    def checkIdAgainstFacebookMe(self, form):
        code = form.secret.data
        resp = self._facebookMe(code)
        if 200 != resp.status:
            raise ReportedError(["Cannot login to facebook"], 403)
        data = json.loads(resp.data)
        if data["id"] != form.identifier.data:
            raise ReportedError(["bad facebook id"], 403)

    def facebookLogin(self, form):
        self.checkIdAgainstFacebookMe(form)
        cred = Credential.get("facebook", form.identifier.data)
        if cred is None:
            raise ReportedError(["You have to register first"], 403)
        return self.finishLogin(cred.user)

    @formValidated(LoginForm, 403)
    @FlaskInterface.exceptionChecked
    def do_login(self,form):
        session['logincred'] = dict(credentialType=form.credentialType.data, identifier = form.identifier.data)
        if form.credentialType.data == 'password':
            return self.passwordLogin(form)
        if form.credentialType.data == 'facebook':
            return self.facebookLogin(form)
        raise ValueError() #not reached

    def contentsOfFileNamedInConfig(self, confkey):
        f = open(app.config.get(confkey))
        ret = f.read()
        f.close()
        return ret

    @formValidated(KeygenForm)
    @FlaskInterface.exceptionChecked
    def do_keygen(self, form):
        email = form.email.data
        spkac = SPKAC(form.pubkey.data, CN=email, Email = email)
        ca_crt = X509.load_cert_string(self.contentsOfFileNamedInConfig("CA_CERTIFICATE_FILE"))
        ca_pkey = EVP.load_key_string(self.contentsOfFileNamedInConfig("CA_KEY_FILE"))
        serial=1
        now = int(time.time())
        notAfter = now + 60 * 60 * 24 * 365 * 2
        cert = spkac.gen_crt(ca_pkey, ca_crt, serial, now, notAfter, 'sha1').as_pem()
        if current_user.is_authenticated():
            identifier, digest = self.parseCert(cert)
            Credential.new(current_user, "certificate", identifier, digest)
        else:
            if form.createUser.data:
                cred = self.registerCertUser(cert, [email])
                self.loginUser(cred.user)
        resp = flask.make_response(cert, 200)
        resp.headers["Content-Type"] = "application/x-x509-user-cert"
        return resp
        

    def parseCert(self, cert):
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName.encode('raw_unicode_escape').decode('utf-8')
        identifier = u"{0}/{1}".format(digest, 
            cn)
        return identifier, digest

    def getEmailFromQueryParameters(self):
        parsed = urlparse.urlparse(request.url)
        email = urlparse.parse_qs(parsed.query).get('email', None)
        return email

    def registerCertUser(self, cert, email):
        if cert is None:
            raise ReportedError(["No certificate given"], 403)
        identifier, digest = self.parseCert(cert)
        cred = Credential.get("certificate", identifier)
        if cred is None:
            if email is None:
                raise ReportedError(["You have to register first"], 403)
            CredentialManager.create_user_with_creds("certificate", identifier, digest, email[0])
            cred = Credential.get("certificate", identifier)
            self.email_verification(cred.user)
        cred.user.activate()
        return cred

    @FlaskInterface.exceptionChecked
    def do_ssl_login(self):
        cert = request.environ.get('SSL_CLIENT_CERT',None)
        email = self.getEmailFromQueryParameters()
        cred = self.registerCertUser(cert, email)
        return self.finishLogin(cred.user)

    @formValidated(DeregisterForm, 400)
    @FlaskInterface.exceptionChecked
    def do_deregister(self,form):
        if not self.isLoginCredentials(form):
            raise ReportedError(["You should use your login credentials to deregister"], 400)
        return self.simple_response('deregistered')

    @FlaskInterface.exceptionChecked
    def do_logout(self):
        logout_user()
        return self.simple_response('logged out')

    def isAnyoneHandAssurredOf(self, anotherUsers):
        for anotherUser in anotherUsers:
            for assurance in Assurance.getByUser(anotherUser):
                if assurance not in [emailVerification]:
                    return True        
        return False

    @formValidated(RegistrationForm)
    @FlaskInterface.exceptionChecked
    def do_registration(self, form):
        additionalInfo = {}
        digest = form.digest.data
        if digest == '':
            digest = None
        if digest is not None:
            anotherUsers = User.getByDigest(form.digest.data)
            if anotherUsers:
                if self.isAnyoneHandAssurredOf(anotherUsers):
                    raise ReportedError([anotherUserUsingYourHash], 400)
                additionalInfo["message"] = anotherUserUsingYourHash
        user = CredentialManager.create_user_with_creds(
            form.credentialType.data,
            form.identifier.data,
            form.secret.data,
            form.email.data,
            digest)
        self.email_verification(user)
        user.set_authenticated()
        user.activate()
        r = login_user(user)
        if r:
            return self.as_dict(user, **additionalInfo)
    
    @FlaskInterface.exceptionChecked
    def do_change_password(self):
        form = PasswordChangeForm()
        if form.validate_on_submit():
            user = current_user
            cred = Credential.getByUser(user, 'password')
            oldSecret = CredentialManager.protect_secret(form.oldPassword.data)
            if cred.secret != oldSecret:
                raise ReportedError(["old password does not match"])
            secret = CredentialManager.protect_secret(form.newPassword.data)
            cred.secret = secret
            cred.save()
            return self.simple_response('password changed succesfully')
        return self.form_validation_error_response(form)
    
    @FlaskInterface.exceptionChecked
    def do_get_by_email(self, email):
        assurances = Assurance.getByUser(current_user)
        if assurances.has_key('assurer'):
            user = User.getByEmail(email)
            if user is None:
                raise ReportedError(["no such user"], status=404)
            return self.as_dict(user)
        raise ReportedError(["no authorization"], status=403)
    
    @formValidated(AssuranceForm)
    @FlaskInterface.exceptionChecked
    def do_add_assurance(self, form):
        assurances = Assurance.getByUser(current_user)
        neededAssurance = form.assurance.data
        assurerAssurance = "assurer.{0}".format(neededAssurance)
        if assurances.has_key('assurer') and assurances.has_key(assurerAssurance):
            if form.email.data:
                user = User.getByEmail(form.email.data)
                if form.digest.data:
                    users = User.getByDigest(form.digest.data)
                    for anotherUser in users:
                        if anotherUser.email != user.email:
                            anotherUser.hash = None
                            anotherUser.save()
            else:
                users = User.getByDigest(form.digest.data)
                if len(users) > 1:
                    raise ReportedError(["Two users with the same hash; specify both hash and email"], 400)  
                user = users[0]                  
            Assurance.new(user, neededAssurance, current_user)
            return self.simple_response("added assurance {0} for {1}".format(neededAssurance, user.email))
        raise ReportedError(["no authorization"], 403)
    
    @FlaskInterface.exceptionChecked
    def do_show_user(self, userid):
        allowed, targetuser = self.isAllowedToGetUser(userid)
        if allowed:
            return self.as_dict(targetuser)
        raise ReportedError(["no authorization"], status=403)
    
    @FlaskInterface.exceptionChecked
    def do_verify_email(self, token):
        cred = Credential.getBySecret('emailcheck', token)
        if cred is None:
            raise ReportedError(["unknown token"], 404)
        if float(cred.identifier) < time.time():
            raise ReportedError(["expired token"], 400)
        user = cred.user
        Assurance.new(user,emailVerification,user)
        cred.rm()
        return self.simple_response("email verified OK")
    
    def _sendResetMail(self, user, secret, expiry):
        timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
        serverName = app.config.get('SERVER_NAME')
        uri = "{0}?secret={1}".format(app.config.get("PASSWORD_RESET_FORM_URL"), secret, user.email)
        text = """Hi, click on <a href="{0}">{0}</a> until {1} to reset your password""".format(uri, timeText)
        subject = "Password Reset for {0}".format(serverName)
        mail.send_message(subject=subject, body=text, recipients=[user.email], sender=app.config.get('SERVER_EMAIL_ADDRESS'))
    
    @FlaskInterface.exceptionChecked
    def do_send_password_reset_email(self, email):
        user = User.getByEmail(email)
        if user is None:
            raise ReportedError(['Invalid email address'])
        secret=unicode(uuid4())
        expiry = time.time()
        Credential.new(user, 'email_for_password_reset', secret, unicode(expiry+14400))
        self._sendResetMail(user, secret, expiry)
        return self.simple_response("Password reset email has successfully sent.")
    
    @formValidated(PasswordResetForm)
    @FlaskInterface.exceptionChecked
    def do_password_reset(self, form):
        credType = 'email_for_password_reset'
        cred = Credential.get(credType, form.secret.data)
        if cred is None or (float(cred.secret) < time.time()):
            Credential.deleteExpired(credType)
            raise ReportedError(['What?'], 404)
        passcred = Credential.getByUser(cred.user, 'password')
        passcred.secret = CredentialManager.protect_secret(form.password.data)
        cred.rm()
        return self.simple_response('Password successfully changed')

    def isLoginCredentials(self, form):
        return session['logincred']['credentialType'] == form.credentialType.data and session['logincred']['identifier'] == form.identifier.data

    @formValidated(CredentialIdentifierForm)
    @FlaskInterface.exceptionChecked
    def do_remove_credential(self, form):
        if self.isLoginCredentials(form):
            raise ReportedError(["You cannot delete the login you are using"], 400)            
        cred=Credential.get(form.credentialType.data, form.identifier.data)
        if cred is None:
            raise ReportedError(['No such credential'], 404)
        cred.rm()
        return self.simple_response('credential removed')

    @formValidated(CredentialForm)
    @FlaskInterface.exceptionChecked
    def do_add_credential(self, form):
        Credential.new(current_user,
            form.credentialType.data,
            form.identifier.data,
            form.secret.data)
        return self.as_dict(current_user)
    
    @formValidated(DigestUpdateForm)
    @FlaskInterface.exceptionChecked
    def do_update_hash(self,form):
        digest = form.digest.data
        if digest == '':
            digest = None
        current_user.hash = digest
        assurances = Assurance.listByUser(current_user)
        for assurance in assurances:
            if assurance.name != emailVerification:
                assurance.rm()
        return self.simple_response('')

    def do_uris(self):
        data = dict(
            BASE_URL = app.config.get('BASE_URL'),
            SSL_LOGIN_URL = app.config.get('SSL_LOGIN_URL'),
        )
        ret = json.dumps(data)
        return self.make_response(ret,200)
