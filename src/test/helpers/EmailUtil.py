from pdoauth.EmailHandling import EmailHandling
from test.helpers.FakeInterFace import FakeInterface, FakeApp, FakeMail,\
    FakeForm
from smtplib import SMTPException
from bs4 import BeautifulSoup
import re
from test.helpers.UserUtil import UserUtil
from test import config
from pdoauth.Messages import emailChangeEmailSent
import json
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User



exampleBody = """Dear abc@xyz.uw,
This is a reset email.
Go to https://local.sso.edemokraciagep.org:8888/static/passwordreset.html?secret=th1s1sth4s3cret
you have to do it until 11 Dec 2098 12:34:56.

Sincerely,
The Test machine
"""

exampleHtml = """<html><head></head><body>
Dear abc@xyz.uw,<br>
This is a reset email.<br/>
Click <a href="https://local.sso.edemokraciagep.org:8888/static/passwordreset.html?secret=th1s1sth4s3cret">Click</a><br/>
you have to do it until 11 Dec 2098 12:34:56.<br/>
<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""

class TestMailer(EmailHandling, FakeInterface):
    app = FakeApp()
    mail = FakeMail()

class FailingMail(FakeMail):
    def send(self,msg):
        raise SMTPException('some smtp error')

class FailingMailer(EmailHandling, FakeInterface):
    app = FakeApp()
    mail = FailingMail()

class EmailUtil(UserUtil):
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
        text = self.outbox[0].html
        soup = BeautifulSoup(text, "lxml")
        passwordResetLink = soup.find("a")['href']
        self.secret = passwordResetLink.split('secret=')[1]
        self.tempcred = Credential.getBySecret('email_for_password_reset',self.secret)
        return passwordResetLink

    def getValidateUri(self):
        return re.search('href="([^"]*)', self.outbox[0].html).group(1)

    def assertEmailContains(self, thingToFind, message):
        self.assertTrue(thingToFind in message.body)
        self.assertTrue(thingToFind in message.html)

    def assertGotAnEmailContaining(self, thingToFind):
        message = self.mailer.mail.outbox[0]
        self.assertEmailContains(thingToFind, message)

    def assertSubjectIs(self, subject):
        return self.assertEqual(self.mailer.mail.outbox[0].subject, subject)

    def doConfirmChangeEmail(self, secret=None, confirm=True, useverifysecret=False):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        if secret is None:
            if useverifysecret:
                secret = Credential.getByUser(self.user, 'changeemailandverify').secret
            else:
                secret = Credential.getByUser(self.user, 'changeemail').secret
        return self.controller.confirmEmailChange(FakeForm(dict(confirm=confirm, secret=secret)))

    def initiateEmailChange(self, client):
        self.login(client)
        csrf = self.getCSRF(client)
        self.newEmail = self.createRandomEmailAddress()
        data = dict(csrf_token=csrf, newemail=self.newEmail)
        resp = client.post(config.BASE_URL + '/v1/emailchange', data=data)
        return resp

    def assertEmailChangeIsInitiated(self, resp):
        text = self.getResponseText(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(emailChangeEmailSent, json.loads(text)['message'])
        user = User.getByEmail(self.userCreationEmail)
        self.userid=user.userid
        tempCredential = Credential.getByUser(user, "changeemail")
        self.secret = tempCredential.secret
        self.assertEqual(self.newEmail, tempCredential.getAdditionalInfo())


