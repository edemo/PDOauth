#pylint: disable=no-member
from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Credential import Credential
from test.helpers.ResponseInfo import ResponseInfo
from test.helpers.RandomUtil import RandomUtil
from test.helpers.FakeInterFace import FakeForm
from bs4 import BeautifulSoup
import re
import time

class UserUtil(ResponseInfo, RandomUtil):

    def addDataBasedOnOptionValue(self, name, optval, default):
        if optval is not False:
            if optval is None:
                token = default
            else:
                token = optval
            self.data[name] = token

    def getCookieParts(self, response):
        cookieHeader = response.headers['Set-Cookie']
        cookieparts = cookieHeader.split(';')
        cookieDict = dict()
        for part in cookieparts:
            key,value = part.split("=")
            cookieDict[key.strip()] = value.strip()
        return cookieDict

    def createUserWithCredentials(self,
            credType='password', userid=None, password=None, email=None):
        self.setupUserCreationData(userid, password, email)
        cred = CredentialManager.create_user_with_creds(
            credType,
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail)
        cred.user.activate()
        return cred

    def createLoggedInUser(self):
        self.setupRandom()
        self.cred = self.createUserWithCredentials()
        self.cred.user.authenticated = True
        self.controller.loginInFramework(self.cred)
        return self.cred

    def deleteUser(self, user):
        for cred in Credential.getByUser(user):
            cred.rm()
        user.rm()

    def assertUserResponse(self, resp):
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(len(data['assurances'].keys()) < 2)
        self.assertTrue("@example.com" in data['email'])
        self.assertTrue(data.has_key('userid'))
        return data

    def showUserByCurrentUser(self, ouserid):
        userid = self.controller.getCurrentUser().userid
        self.controller.getSession()['auth_user'] =  (userid, userid)
        resp = self.controller.doShowUser(userid=ouserid)
        return resp

    def prepareLoginForm(self, inactive = False, identifier = None, secret=None):
        cred = self.createUserWithCredentials()
        if inactive:
            cred.user.active=False
        self.data = dict(credentialType='password',
            identifier=None,
            password=None)
        self.addDataBasedOnOptionValue('identifier', identifier, self.userCreationUserid)
        self.addDataBasedOnOptionValue('password', secret, self.usercreationPassword)
        form = FakeForm(self.data)
        return form

    def _sendPasswordResetEmail(self, email=None):
        self.createUserWithCredentials()
        if email is None:
            email = self.userCreationEmail
        resp = self.controller.doSendPasswordResetEmail(email)
        self.data = self.fromJson(resp)
        self.outbox = self.controller.mail.outbox
        return resp.status_code

    def the_reset_link_is_in_the_reset_email(self):
        self._sendPasswordResetEmail()
        text = unicode(self.outbox[0].html)
        soup = BeautifulSoup(text)
        passwordResetLink = soup.find("a")['href']
        self.secret = passwordResetLink.split('?secret=')[1]
        self.tempcred = Credential.getBySecret('email_for_password_reset',self.secret)
        return passwordResetLink

    def getValidateUri(self):
        return re.search('href="([^"]*)', self.outbox[0].html).group(1)

    def assertEmailContains(self, thingToFind, message):
        self.assertTrue(thingToFind in unicode(message.body))
        self.assertTrue(thingToFind in unicode(message.html))

    def assertGotAnEmailContaining(self, thingToFind):
        message = self.mailer.mail.outbox[0]
        self.assertEmailContains(thingToFind, message)

    def assertSubjectIs(self, subject):
        return self.assertEqual(self.mailer.mail.outbox[0].subject, subject)

    def countExpiredCreds(self, credentialType = 'email_for_password_reset'):
        expiredcreds = []
        now = time.time()
        creds = Credential.query.filter_by(credentialType=credentialType) # @UndefinedVariable
        for client in creds:
            if client.getExpirationTime() < now:
                expiredcreds.append(client)
        return len(expiredcreds)

