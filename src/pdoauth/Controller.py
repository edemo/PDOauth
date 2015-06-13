from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance, emailVerification
from pdoauth.CredentialManager import CredentialManager
from uuid import uuid4
import time
from flask import json
from pdoauth.ReportedError import ReportedError
from pdoauth.WebInterface import WebInterface
from pdoauth.EmailHandling import EmailHandling
from pdoauth.LoginHandling import LoginHandling
from pdoauth.CertificateHandling import CertificateHandling
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from urllib import urlencode

anotherUserUsingYourHash = "another user is using your hash"
passwordResetCredentialType = 'email_for_password_reset'

class Controller(WebInterface, EmailHandling, LoginHandling,  CertificateHandling):
    LOGIN_CREDENTIAL_ATTRIBUTE = 'logincred'
    def setAuthUser(self, userid, isHerself):
        self.getSession()['auth_user']=(userid, isHerself)

    def authenticateUserOrBearer(self):
        authHeader = self.getHeader('Authorization')
        current_user = self.getCurrentUser()
        if current_user.is_authenticated():
            self.setAuthUser(current_user.userid, True)
        elif authHeader:
            token = authHeader.split(" ")[1]
            data = TokenInfoByAccessKey.find(token)
            targetuserid = data.tokeninfo.user_id
            self.setAuthUser(targetuserid, False)
        else:
            raise ReportedError(["no authorization"], status=403)

    def redirectIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            resp = self.error_response(["authentication needed"], 302)
            uri = "{1}?{0}".format(urlencode({"next": self.getRequest().url}), self.app.config.get("START_URL"))
            resp.headers['Location'] = uri
            return resp


    def jsonErrorIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            raise ReportedError(["not logged in"], status=403)


    def setLoginCredentialIntoSession(self, credentialType, identifier):
        self.getSession()[self.LOGIN_CREDENTIAL_ATTRIBUTE] = dict(credentialType=credentialType, identifier=identifier)
        return credentialType

    def do_login(self,form):
        credentialType = form.credentialType.data
        credentialType = self.setLoginCredentialIntoSession(credentialType, form.identifier.data)
        if credentialType == 'password':
            return self.passwordLogin(form)
        if credentialType == 'facebook':
            return self.facebookLogin(form)

    def do_logout(self):
        self.logOut()
        return self.simple_response('logged out')

    def do_deregister(self,form):
        if not self.isLoginCredentials(form):
            raise ReportedError(["You should use your login credentials to deregister"], 400)
        cred = Credential.get(form.credentialType.data, form.identifier.data)
        user = cred.user
        creds = Credential.getByUser(user)
        for cred in creds:
            cred.rm()
        assurances = Assurance.listByUser(user)
        for assurance in assurances:
            assurance.rm()
        user.rm()
        return self.simple_response('deregistered')

    def isAnyoneHandAssurredOf(self, anotherUsers):
        for anotherUser in anotherUsers:
            for assurance in Assurance.getByUser(anotherUser):
                if assurance not in [emailVerification]:
                    return True        
        return False

    def do_registration(self, form):
        return self._do_registration(form)

    def _do_registration(self, form):
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
        self.sendPasswordVerificationEmail(user)
        user.set_authenticated()
        user.activate()
        r = self.loginUserInFramework(user)
        if r:
            return self.returnUserAndLoginCookie(user, additionalInfo)
    
    def do_change_password(self, form):
            user = self.getCurrentUser()
            cred = Credential.getByUser(user, 'password')
            oldSecret = CredentialManager.protect_secret(form.oldPassword.data)
            if cred.secret != oldSecret:
                raise ReportedError(["old password does not match"])
            secret = CredentialManager.protect_secret(form.newPassword.data)
            cred.secret = secret
            cred.save()
            return self.simple_response('password changed succesfully')
    
    def do_get_by_email(self, email):
        return self._do_get_by_email(email)

    def _do_get_by_email(self, email):
        assurances = Assurance.getByUser(self.getCurrentUser())
        if assurances.has_key('assurer'):
            user = User.getByEmail(email)
            if user is None:
                raise ReportedError(["no such user"], status=404)
            return self.as_dict(user)
        raise ReportedError(["no authorization"], status=403)
    
    def deleteDigestFromOtherUsers(self, user, digest):
        if digest:
            users = User.getByDigest(digest)
            for anotherUser in users:
                if anotherUser.email != user.email:
                    anotherUser.hash = None
                    anotherUser.save()

    def assureExactlyOneUserInList(self, users):
        if len(users) == 0:
            raise ReportedError('No user with this hash', 400)
        if len(users) > 1:
            raise ReportedError(["More users with the same hash; specify both hash and email"], 400)


    def checkUserAgainsDigest(self, digest, user):
        if digest is not None and user.hash != digest:
            raise ReportedError('This user does not have that digest', 400)

    def getUserForEmailAndOrHash(self, digest, email):
        if email:
            user = User.getByEmail(email)
            self.deleteDigestFromOtherUsers(user, digest)
            self.checkUserAgainsDigest(digest, user)
            return user
        users = User.getByDigest(digest)
        self.assureExactlyOneUserInList(users)
        return users[0]

    def assureUserHaveTheGivingAssurancesFor(self, neededAssurance):
        assurances = Assurance.getByUser(self.getCurrentUser())
        assurerAssurance = "assurer.{0}".format(neededAssurance)
        if not (assurances.has_key('assurer') and assurances.has_key(assurerAssurance)):
            raise ReportedError(["no authorization"], 403)

    def do_add_assurance(self, form):
        neededAssurance = form.assurance.data
        self.assureUserHaveTheGivingAssurancesFor(neededAssurance)
        user = self.getUserForEmailAndOrHash(form.digest.data, form.email.data)                  
        Assurance.new(user, neededAssurance, self.getCurrentUser())
        return self.simple_response("added assurance {0} for {1}".format(neededAssurance, user.email))

    def getShownUser(self, userid, authuser, isHerself):
        if userid == 'me':
            shownUser = authuser
        elif isHerself:
            if Assurance.getByUser(authuser).has_key('assurer'):
                shownUser = User.get(userid)
            else:
                raise ReportedError(["no authorization to show other users"], status=403)
        else:
            raise ReportedError(["no authorization to show other users"], status=403)
        return shownUser


    def getAuthenticatedUser(self):
        authid, isHerself = self.getSession()['auth_user']
        authuser = User.get(authid)
        return authuser, isHerself

    def do_show_user(self, userid):
        authuser, isHerself = self.getAuthenticatedUser()
        shownUser = self.getShownUser(userid, authuser, isHerself)
        return self.as_dict(shownUser)
    
    def checkEmailverifyCredential(self, cred):
        if cred is None:
            raise ReportedError(["unknown token"], 404)
        if float(cred.identifier) < time.time():
            raise ReportedError(["expired token"], 400)

    def getCredentialForEmailverifyToken(self, token):
        cred = Credential.getBySecret('emailcheck', token)
        return cred

    def do_verify_email(self, token):
        cred = self.getCredentialForEmailverifyToken(token)
        self.checkEmailverifyCredential(cred)
        user = cred.user
        Assurance.new(user,emailVerification,user)
        cred.rm()
        return self.simple_response("email verified OK")
    
    def do_send_password_reset_email(self, email):
        user = User.getByEmail(email)
        if user is None:
            raise ReportedError(['Invalid email address'])
        passwordResetEmailExpiration = 14400
        secret=unicode(uuid4())
        expirationTime = time.time() + passwordResetEmailExpiration
        Credential.new(user, passwordResetCredentialType, secret, unicode(expirationTime))
        self.sendPasswordResetMail(user, secret, expirationTime)
        return self.simple_response("Password reset email has successfully sent.")
    
    def do_password_reset(self, form):
        cred = Credential.get(passwordResetCredentialType, form.secret.data)
        if cred is None or (float(cred.secret) < time.time()):
            Credential.deleteExpired(passwordResetCredentialType)
            raise ReportedError(['The secret has expired'], 404)
        passcred = Credential.getByUser(cred.user, 'password')
        passcred.secret = CredentialManager.protect_secret(form.password.data)
        cred.rm()
        return self.simple_response('Password successfully changed')

    def isLoginCredentials(self, form):
        session = self.getSession()
        if not session.has_key(self.LOGIN_CREDENTIAL_ATTRIBUTE):
            raise ReportedError(["Internal error: no login credential found"], 500)
        return session[self.LOGIN_CREDENTIAL_ATTRIBUTE]['credentialType'] == form.credentialType.data and session[self.LOGIN_CREDENTIAL_ATTRIBUTE]['identifier'] == form.identifier.data

    def do_remove_credential(self, form):
        if self.isLoginCredentials(form):
            raise ReportedError(["You cannot delete the login you are using"], 400)            
        cred=Credential.get(form.credentialType.data, form.identifier.data)
        if cred is None:
            raise ReportedError(['No such credential'], 404)
        cred.rm()
        return self.simple_response('credential removed')

    def do_add_credential(self, form):
        user = self.getCurrentUser()
        Credential.new(user,
            form.credentialType.data,
            form.identifier.data,
            form.secret.data)
        return self.as_dict(user)
    
    def deleteHandAssuredAssurances(self, assurances):
        for assurance in assurances:
            if assurance.name != emailVerification:
                assurance.rm()

    def do_update_hash(self,form):
        digest = form.digest.data
        if digest == '':
            digest = None
        user = self.getCurrentUser()
        user.hash = digest
        user.save()
        assurances = Assurance.listByUser(user)
        self.deleteHandAssuredAssurances(assurances)
        return self.simple_response('new hash registered')

    def do_uris(self):
        data = dict(
            BASE_URL = self.getConfig('BASE_URL'),
            START_URL = self.getConfig('START_URL'),
            PASSWORD_RESET_FORM_URL = self.getConfig('PASSWORD_RESET_FORM_URL'),
            SSL_LOGIN_BASE_URL = self.getConfig('SSL_LOGIN_BASE_URL'),
            SSL_LOGOUT_URL = self.getConfig('SSL_LOGOUT_URL'),
        )
        ret = json.dumps(data)
        return self.make_response(ret,200)
