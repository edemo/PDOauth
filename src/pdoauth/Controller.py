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
from pdoauth.Responses import Responses

class Controller(WebInterface, Responses, EmailHandling, LoginHandling,  CertificateHandling):
    anotherUserUsingYourHash = "another user is using your hash"
    passwordResetCredentialType = 'email_for_password_reset'

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

    def do_login(self,form):
        credentialType = form.credentialType.data
        if credentialType == 'password':
            return self.passwordLogin(form)
        if credentialType == 'facebook':
            return self.facebookLogin(form)

    def do_logout(self):
        self.logOut()
        return self.simple_response('logged out')

    def do_deregister(self,form):
        self.sendDeregisterMail(self.getCurrentUser())
        return self.simple_response('deregistration email has been sent')

    def removeCredentials(self, user):
        creds = Credential.getByUser(user)
        for cred in creds:
            cred.rm()

    def removeAssurances(self, user):
        assurances = Assurance.listByUser(user)
        for assurance in assurances:
            assurance.rm()

    def removeUser(self, user):
        self.removeCredentials(user)
        self.removeAssurances(user)
        user.rm()

    def do_deregistration_doit(self, form):
        secret = form.deregister_secret.data
        if secret is not None:
            deregistrationCredential = Credential.getBySecret('deregister', secret)
            if deregistrationCredential is None:
                raise ReportedError(["bad deregistration secret"],400)
            user = deregistrationCredential.user
            self.removeUser(user)
            return self.simple_response('you are deregistered')
        raise ReportedError(["secret is needed for deregistration_doit"],400)

    def isAnyoneHandAssurredOf(self, anotherUsers):
        for anotherUser in anotherUsers:
            for assurance in Assurance.getByUser(anotherUser):
                if assurance not in [emailVerification]:
                    return True        
        return False

    def do_registration(self, form):
        additionalInfo = {}
        digest = form.digest.data
        if digest == '':
            digest = None
        if digest is not None:
            anotherUsers = User.getByDigest(form.digest.data)
            if anotherUsers:
                if self.isAnyoneHandAssurredOf(anotherUsers):
                    raise ReportedError([self.anotherUserUsingYourHash], 400)
                additionalInfo["message"] = self.anotherUserUsingYourHash
        cred = CredentialManager.create_user_with_creds(
            form.credentialType.data,
            form.identifier.data,
            form.secret.data,
            form.email.data,
            digest)
        user = cred.user
        self.sendPasswordVerificationEmail(user)
        user.set_authenticated()
        user.activate()
        r = self.loginInFramework(cred)
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
        current_user = self.getCurrentUser()
        assurances = Assurance.getByUser(current_user)
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
            raise ReportedError(['No user with this hash'], 400)
        if len(users) > 1:
            raise ReportedError(["More users with the same hash; specify both hash and email"], 400)


    def checkUserAgainsDigest(self, digest, user):
        if digest is not None and user.hash != digest:
            raise ReportedError(['This user does not have that digest'], 400)

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
        Credential.new(user, self.passwordResetCredentialType, secret, unicode(expirationTime))
        self.sendPasswordResetMail(user, secret, expirationTime)
        return self.simple_response("Password reset email has successfully sent.")
    
    def do_password_reset(self, form):
        cred = Credential.get(self.passwordResetCredentialType, form.secret.data)
        if cred is None or (float(cred.secret) < time.time()):
            Credential.deleteExpired(self.passwordResetCredentialType)
            raise ReportedError(['The secret has expired'], 404)
        passcred = Credential.getByUser(cred.user, 'password')
        passcred.secret = CredentialManager.protect_secret(form.password.data)
        cred.rm()
        return self.simple_response('Password successfully changed')

    def do_remove_credential(self, form):
        session = self.getSession()
        if session['login_credential'] == (form.credentialType.data, form.identifier.data):
            raise ReportedError(["You cannot delete the login you are using"],400)
        cred=Credential.get(form.credentialType.data, form.identifier.data)
        if cred is None:
            raise ReportedError(['No such credential'], 404)
        cred.rm()
        return self.simple_response('credential removed')

    def do_add_credential(self, form):
        user = self.getCurrentUser()
        CredentialManager.addCredToUser(user,
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
