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
from pdoauth.Statistics import Statistics
from pdoauth.Messages import badAuthHeader, noAuthorization,\
    authenticationNeeded, notLoggedIn, loggedOut, deregistrationEmailSent,\
    secretIsNeededForDeregistrationDoit, badDeregistrationSecret,\
    youAreDeregistered, anotherUserUsingYourHash, newHashRegistered,\
    passwordChangedSuccessfully, noSuchUser, noUserWithThisHash,\
    moreUsersWarning, oldPasswordDoesNotMatch, thisUserDoesNotHaveThatDigest,\
    addedAssurance, noShowAuthorization, unknownToken, expiredToken,\
    emailVerifiedOK, invalidEmailAdress, passwordResetSent, theSecretHasExpired,\
    passwordSuccessfullyChanged, cannotDeleteLoginCred, noSuchCredential,\
    credentialRemoved, sameHash, verificationEmailSent

class Controller(
        WebInterface, Responses, EmailHandling,
        LoginHandling,  CertificateHandling,
        Statistics):

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
                raise ReportedError([badAuthHeader,authHeader], status=403)
            token = headerSplit[1]
            tokeninfo = TokenInfoByAccessKey.find(token).tokeninfo
            appid = tokeninfo.client_id
            targetuserid = tokeninfo.user_id
            self.setAuthUser(targetuserid, appid)
        else:
            raise ReportedError([noAuthorization], status=403)

    def redirectIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            resp = self.error_response([authenticationNeeded], 302)
            startUrl = self.app.config.get("LOGIN_URL")
            nextArg = {"next":self.getRequest().url}
            uri = "{1}?{0}".format(urlencode(nextArg), startUrl)
            resp.headers['Location'] = uri
            return resp

    def jsonErrorIfNotLoggedIn(self):
        if not self.getCurrentUser().is_authenticated():
            raise ReportedError([notLoggedIn], status=403)

    def doLogin(self,form):
        credentialType = form.credentialType.data
        if credentialType == 'password':
            return self.passwordLogin(form)
        if credentialType == 'facebook':
            return self.facebookLogin(form)

    def doLogout(self):
        self.logOut()
        return self.simple_response(loggedOut)

    def doDeregister(self,form):
        self.sendDeregisterMail(self.getCurrentUser())
        return self.simple_response(deregistrationEmailSent)

    def removeCredentials(self, user):
        creds = Credential.getByUser(user)
        for cred in creds:
            cred.rm()

    def removeAssurances(self, user):
        assurances = Assurance.listByUser(user)
        for assurance in assurances:
            assurance.rm()


    def removeAppMaps(self, user):
        for appmap in AppMap.getForUser(user):
            appmap.rm()

    def removeUser(self, user):
        self.removeCredentials(user)
        self.removeAssurances(user)
        self.removeAppMaps(user)
        user.rm()

    def doDeregistrationDoit(self, form):
        Credential.deleteExpired('deregister')
        secret = form.deregister_secret.data
        if secret is None:
            raise ReportedError(
                [secretIsNeededForDeregistrationDoit],400)
        deregistrationCredential = Credential.getBySecret('deregister', secret)
        if deregistrationCredential is None:
            raise ReportedError([badDeregistrationSecret],400)
        user = deregistrationCredential.user
        self.removeUser(user)
        return self.simple_response(youAreDeregistered)

    def isAnyoneHandAssurredOf(self, anotherUsers):
        for anotherUser in anotherUsers:
            for assurance in Assurance.getByUser(anotherUser):
                if assurance not in [emailVerification]:
                    return True
        return False



    def updateHashAndAssurances(self, user, digest):
        user.hash = digest
        assurances = Assurance.listByUser(user)
        self.deleteHandAssuredAssurances(assurances)
        if digest is not None:
            Assurance.new(user, "hashgiven", user)
        user.save()


    def checkHashInOtherUsers(self, user, additionalInfo, digest):
        if digest is None:
            return
        anotherUsers = User.getByDigest(digest)
        if anotherUsers:
            if self.isAnyoneHandAssurredOf(anotherUsers):
                self.sendHashCollisionMail(user)
                self.removeUser(user)
                raise ReportedError([anotherUserUsingYourHash])
            additionalInfo["message"] = anotherUserUsingYourHash

    def checkAndUpdateHash(self, form, user):
        additionalInfo = dict()
        digest = form.digest.data
        if digest == '':
            digest = None
        if (digest is not None) and (user.hash == digest):
            additionalInfo["message"] = sameHash
        else:
            self.checkHashInOtherUsers(user, additionalInfo, digest)
            self.updateHashAndAssurances(user, digest)
        return additionalInfo

    def doUpdateHash(self,form):
        user = self.getCurrentUser()
        additionalInfo  = self.checkAndUpdateHash(form,user)
        return self.simple_response(newHashRegistered, additionalInfo)

    def doRegistration(self, form):
        Credential.deleteExpired('emailcheck')
        cred = CredentialManager.create_user_with_creds(
            form.credentialType.data,
            form.identifier.data,
            form.password.data,
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
            raise ReportedError([oldPasswordDoesNotMatch])
        secret = CredentialManager.protect_secret(form.newPassword.data)
        cred.secret = secret
        cred.save()
        return self.simple_response(passwordChangedSuccessfully)

    def doGetByEmail(self, email):
        current_user = self.getCurrentUser()
        assurances = Assurance.getByUser(current_user)
        if assurances.has_key('assurer'):
            user = User.getByEmail(email)
            if user is None:
                raise ReportedError([noSuchUser], status=404)
            return self.as_dict(user)
        raise ReportedError([noAuthorization], status=403)

    def deleteDigestFromOtherUsers(self, user, digest):
        if digest:
            users = User.getByDigest(digest)
            for anotherUser in users:
                if anotherUser.email != user.email:
                    anotherUser.hash = None
                    anotherUser.save()

    def assureExactlyOneUserInList(self, users):
        if len(users) == 0:
            raise ReportedError([noUserWithThisHash], 400)
        if len(users) > 1:
            raise ReportedError([moreUsersWarning], 400)


    def checkUserAgainsDigest(self, digest, user):
        if digest is not None and user.hash != digest:
            raise ReportedError([thisUserDoesNotHaveThatDigest], 400)

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
            raise ReportedError([noAuthorization], 403)

    def doAddAssurance(self, form):
        neededAssurance = form.assurance.data
        self.assureUserHaveTheGivingAssurancesFor(neededAssurance)
        user = self.getUserForEmailAndOrHash(
                form.digest.data, form.email.data)
        Assurance.new(user, neededAssurance, self.getCurrentUser())
        msg = '["{2}","{0}","{1}"]'.format(neededAssurance, user.email,addedAssurance)
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
        if not user:
                raise ReportedError([noSuchUser], status=404)
        if self.doesUserAskOwnData(userid, authenticator):
            return self.shownDataForUser(user)
        if self.doesUserAskForOthersData(authuser, authenticator):
            assurances = Assurance.getByUser(authuser)
            if assurances.has_key('assurer'):
                return self.shownDataForAssurer(user)
            else:
                raise ReportedError([noShowAuthorization], status=403)
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
            raise ReportedError([unknownToken], 404)
        if cred.getExpirationTime() < time.time():
            raise ReportedError([expiredToken], 400)

    def getCredentialForEmailverifyToken(self, token):
        cred = Credential.getBySecret('emailcheck', token)
        return cred

    def sendVerifyEmail(self):
        current_user = self.getCurrentUser()
        self.sendPasswordVerificationEmail(current_user)
        return self.simple_response(verificationEmailSent)
        

    def doverifyEmail(self, token):
        cred = self.getCredentialForEmailverifyToken(token)
        self.checkEmailverifyCredential(cred)
        user = cred.user
        Assurance.new(user,emailVerification,user)
        cred.rm()
        return self.simple_response(emailVerifiedOK)

    def doSendPasswordResetEmail(self, email):
        user = User.getByEmail(email)
        if user is None:
            raise ReportedError([invalidEmailAdress])
        self.sendPasswordResetMail(user)
        return self.simple_response(passwordResetSent)

    def doPasswordReset(self, form):
        Credential.deleteExpired(self.passwordResetCredentialType)
        cred = Credential.getBySecret(
            self.passwordResetCredentialType, form.secret.data)
        if cred is None or (cred.getExpirationTime() < time.time()):
            raise ReportedError([theSecretHasExpired], 404)
        passcred = Credential.getByUser(cred.user, 'password')
        protectedSecret = CredentialManager.protect_secret(form.password.data)
        if not passcred:
            passcred = Credential.new(cred.user, "password", cred.user.email, protectedSecret)
        else:
            passcred.secret = protectedSecret
        cred.rm()
        return self.simple_response(passwordSuccessfullyChanged)


    def isLoginCredential(self, form, session):
        loginCredential = session['login_credential']
        credentialFromForm = form.credentialType.data, form.identifier.data
        return loginCredential == credentialFromForm

    def doRemoveCredential(self, form):
        session = self.getSession()
        if self.isLoginCredential(form, session):
            raise ReportedError([cannotDeleteLoginCred],400)
        cred=Credential.get(form.credentialType.data, form.identifier.data)
        if cred is None:
            raise ReportedError([noSuchCredential], 404)
        cred.rm()
        return self.simple_response(credentialRemoved)

    def doAddCredential(self, form):
        user = self.getCurrentUser()
        CredentialManager.addCredToUser(user,
            form.credentialType.data,
            form.identifier.data,
            form.password.data)
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
            LOGIN_URL = self.getConfig('LOGIN_URL'),
            PASSWORD_RESET_FORM_URL = self.getConfig('PASSWORD_RESET_FORM_URL'),
            SSL_LOGIN_BASE_URL = self.getConfig('SSL_LOGIN_BASE_URL'),
            SSL_LOGOUT_URL = self.getConfig('SSL_LOGOUT_URL'),
            ANCHOR_URL = self.getConfig('ANCHOR_URL'),
            FACEBOOK_APP_ID = self.getConfig('FACEBOOK_APP_ID'),
        )
        ret = json.dumps(data)
        return self.make_response(ret,200)
