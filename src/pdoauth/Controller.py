#pylint: disable=no-member
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance, emailVerification
from pdoauth.CredentialManager import CredentialManager
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
from pdoauth.models.Application import Application
from pdoauth.models.AppMap import AppMap
from pdoauth.models.AppAssurance import AppAssurance

class Controller(
        WebInterface, Responses, EmailHandling,
        LoginHandling,  CertificateHandling):
    anotherUserUsingYourHash = "another user is using your hash"
    moreUsersWarning = \
        "More users with the same hash; specify both hash and email"
    noShowAuthorization = "no authorization to show other users"
    passwordResetSent = "Password reset email has successfully sent."
    cannotDeleteLoginCred = "You cannot delete the login you are using"

    def setAuthUser(self, userid, authenticator):
        self.getSession()['auth_user']=(userid, authenticator)

    def authenticateUserOrBearer(self):
        authHeader = self.getHeader('Authorization')
        current_user = self.getCurrentUser()
        if current_user.is_authenticated():
            self.setAuthUser(current_user.userid, current_user.userid)
        elif authHeader:
            headerSplit = authHeader.split(" ")
            if len(headerSplit)!= 2:
                raise ReportedError(["bad Authorization header",authHeader], status=403)
            token = headerSplit[1]
            tokeninfo = TokenInfoByAccessKey.find(token).tokeninfo
            appid = tokeninfo.client_id
            targetuserid = tokeninfo.user_id
            self.setAuthUser(targetuserid, appid)
        else:
            raise ReportedError(["no authorization"], status=403)

    def redirectIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            resp = self.error_response(["authentication needed"], 302)
            startUrl = self.app.config.get("START_URL")
            nextArg = {"next":self.getRequest().url}
            uri = "{1}?{0}".format(urlencode(nextArg), startUrl)
            resp.headers['Location'] = uri
            return resp

    def jsonErrorIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            raise ReportedError(["not logged in"], status=403)

    def doLogin(self,form):
        credentialType = form.credentialType.data
        if credentialType == 'password':
            return self.passwordLogin(form)
        if credentialType == 'facebook':
            return self.facebookLogin(form)

    def doLogout(self):
        self.logOut()
        return self.simple_response('logged out')

    def doDeregister(self,form):
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

    def doDeregistrationDoit(self, form):
        secret = form.deregister_secret.data
        if secret is None:
            raise ReportedError(
                ["secret is needed for deregistration_doit"],400)
        deregistrationCredential = Credential.getBySecret('deregister', secret)
        if deregistrationCredential is None:
            raise ReportedError(["bad deregistration secret"],400)
        user = deregistrationCredential.user
        self.removeUser(user)
        return self.simple_response('you are deregistered')

    def isAnyoneHandAssurredOf(self, anotherUsers):
        for anotherUser in anotherUsers:
            for assurance in Assurance.getByUser(anotherUser):
                if assurance not in [emailVerification]:
                    return True
        return False


    def checkAndUpdateHash(self, form, user):
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
        user.hash = digest
        user.save()
        assurances = Assurance.listByUser(user)
        self.deleteHandAssuredAssurances(assurances)
        if digest is not None:
            Assurance.new(user, "hashgiven", user)
        return additionalInfo

    def doUpdateHash(self,form):
        user = self.getCurrentUser()
        additionalInfo  = self.checkAndUpdateHash(form,user)
        return self.simple_response('new hash registered', additionalInfo)

    def doRegistration(self, form):
        cred = CredentialManager.create_user_with_creds(
            form.credentialType.data,
            form.identifier.data,
            form.secret.data,
            form.email.data,
            None)
        user = cred.user
        additionalInfo = self.checkAndUpdateHash(form, user)
        self.sendPasswordVerificationEmail(user)
        user.set_authenticated()
        user.activate()
        success = self.loginInFramework(cred)
        if success:
            return self.returnUserAndLoginCookie(user, additionalInfo)

    def doChangePassword(self, form):
        user = self.getCurrentUser()
        cred = Credential.getByUser(user, 'password')
        oldSecret = CredentialManager.protect_secret(form.oldPassword.data)
        if cred.secret != oldSecret:
            raise ReportedError(["old password does not match"])
        secret = CredentialManager.protect_secret(form.newPassword.data)
        cred.secret = secret
        cred.save()
        return self.simple_response('password changed succesfully')

    def doGetByEmail(self, email):
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
            raise ReportedError([self.moreUsersWarning], 400)


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


    def isAssuredToAddAssurance(self, assurances, neededAssurance):
        assurerAssurance = "assurer.{0}".format(neededAssurance)
        isAssurer = assurances.has_key('assurer')
        return isAssurer and assurances.has_key(assurerAssurance)

    def assureUserHaveTheGivingAssurancesFor(self, neededAssurance):
        assurances = Assurance.getByUser(self.getCurrentUser())
        if not self.isAssuredToAddAssurance(assurances, neededAssurance):
            raise ReportedError(["no authorization"], 403)

    def doAddAssurance(self, form):
        neededAssurance = form.assurance.data
        self.assureUserHaveTheGivingAssurancesFor(neededAssurance)
        user = self.getUserForEmailAndOrHash(
                form.digest.data, form.email.data)
        Assurance.new(user, neededAssurance, self.getCurrentUser())
        msg = "added assurance {0} for {1}".format(neededAssurance, user.email)
        return self.simple_response(msg)


    def getAuthenticatedUser(self):
        authid, authenticator = self.getSession()['auth_user']
        authuser = User.get(authid)
        return authuser, authenticator

    def doesUserAskOwnData(self, userid, authenticator):
        return userid == authenticator

    def doesUserAskForOthersData(self, authuser, authenticator):
        return authuser.userid == authenticator

    def computeAssurancesForApp(self, user, app):
        appAssurances = AppAssurance.get(app)
        userAssurances = Assurance.listByUser(user)
        shownAssurances = list()
        for userAssurance in userAssurances:
            if userAssurance.name in appAssurances:
                shownAssurances.append(userAssurance.name)
        return shownAssurances

    def shownDataForApp(self, user, authenticator):
        app = Application.get(authenticator)
        appmapEntry = AppMap.get(app, user)
        shownEmail = appmapEntry.getEmail()
        shownUserId = appmapEntry.userid
        shownAssurances = self.computeAssurancesForApp(user, app)
        return dict(
            email=shownEmail,
            userid=shownUserId,
            assurances=shownAssurances)


    def shownDataForAssurer(self, user):
        return dict(
            email=user.email,
            userid=user.userid,
            assurances=Assurance.getByUser(user),
            hash=user.hash,
            credentials=Credential.getByUser_as_dictlist(user))

    def shownDataForUser(self, user):
        return dict(
            email=user.email,
            userid=user.userid,
            assurances=Assurance.getByUser(user),
            hash=user.hash,
            credentials=Credential.getByUser_as_dictlist(user))

    def getDataOfUserForAuthenticator(self, userid, authuser, authenticator):
        user = User.get(userid)
        if self.doesUserAskOwnData(userid, authenticator):
            return self.shownDataForUser(user)
        if self.doesUserAskForOthersData(authuser, authenticator):
            assurances = Assurance.getByUser(authuser)
            if assurances.has_key('assurer'):
                return self.shownDataForAssurer(user)
            else:
                raise ReportedError([self.noShowAuthorization], status=403)
        return self.shownDataForApp(user, authenticator)

    def doShowUser(self, userid):
        authuser, authenticator = self.getAuthenticatedUser()
        if userid == 'me':
            userid = authuser.userid
        data = self.getDataOfUserForAuthenticator(userid, authuser, authenticator)
        ret = json.dumps(data)
        return self.make_response(ret,200)

    def checkEmailverifyCredential(self, cred):
        if cred is None:
            raise ReportedError(["unknown token"], 404)
        if cred.getExpirationTime() < time.time():
            raise ReportedError(["expired token"], 400)

    def getCredentialForEmailverifyToken(self, token):
        cred = Credential.getBySecret('emailcheck', token)
        return cred

    def doverifyEmail(self, token):
        cred = self.getCredentialForEmailverifyToken(token)
        self.checkEmailverifyCredential(cred)
        user = cred.user
        Assurance.new(user,emailVerification,user)
        cred.rm()
        return self.simple_response("email verified OK")

    def doSendPasswordResetEmail(self, email):
        user = User.getByEmail(email)
        if user is None:
            raise ReportedError(['Invalid email address'])
        self.sendPasswordResetMail(user)
        return self.simple_response(self.passwordResetSent)

    def doPasswordReset(self, form):
        cred = Credential.getBySecret(
            self.passwordResetCredentialType, form.secret.data)
        if cred is None or (cred.getExpirationTime() < time.time()):
            Credential.deleteExpired(self.passwordResetCredentialType)
            raise ReportedError(['The secret has expired'], 404)
        passcred = Credential.getByUser(cred.user, 'password')
        passcred.secret = CredentialManager.protect_secret(form.password.data)
        cred.rm()
        return self.simple_response('Password successfully changed')


    def isLoginCredential(self, form, session):
        loginCredential = session['login_credential']
        credentialFromForm = form.credentialType.data, form.identifier.data
        return loginCredential == credentialFromForm

    def doRemoveCredential(self, form):
        session = self.getSession()
        if self.isLoginCredential(form, session):
            raise ReportedError([self.cannotDeleteLoginCred],400)
        cred=Credential.get(form.credentialType.data, form.identifier.data)
        if cred is None:
            raise ReportedError(['No such credential'], 404)
        cred.rm()
        return self.simple_response('credential removed')

    def doAddCredential(self, form):
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

    def doUris(self):
        data = dict(
            BASE_URL = self.getConfig('BASE_URL'),
            BACKEND_PATH = self.getConfig('BACKEND_PATH'),
            START_URL = self.getConfig('START_URL'),
            PASSWORD_RESET_FORM_URL = self.getConfig('PASSWORD_RESET_FORM_URL'),
            SSL_LOGIN_BASE_URL = self.getConfig('SSL_LOGIN_BASE_URL'),
            SSL_LOGOUT_URL = self.getConfig('SSL_LOGOUT_URL'),
            ANCHOR_URL = self.getConfig('ANCHOR_URL'),
            FACEBOOK_APP_ID = self.getConfig('FACEBOOK_APP_ID'),
        )
        ret = json.dumps(data)
        return self.make_response(ret,200)
