from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.models import Credential
from pdoauth.CredentialManager import CredentialManager
from test.helpers.EmailUtil import TestMailer, EmailUtil
from pdoauth.EmailHandling import EmailHandling
from pdoauth.WebInterface import WebInterface
from test.helpers.FakeInterFace import FakeInterface, FakeApp

class EmailChange(EmailHandling, WebInterface):
    def emailChangeInit(self, newEmailAddress, user):
        secret, expiry = CredentialManager.createTemporaryCredential(user, "changeemail")
        self.sendEmail(user, secret, expiry, "PASSWORD_VERIFICATION")

class EmailChangeTest(PDUnitTest, EmailUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials().user
        self.newEmailAddress = "email{0}@example.com".format(self.randString)
        self.controller = EmailChange(FakeInterface())
        self.controller.app = FakeApp()
        self.controller.mail = TestMailer()

    @test
    def emailChangeInit_creates_a_temporary_credential(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertNotEqual(None, Credential.getByUser(self.user, "changeemail"))

    @test
    def emailChangeInit_send_email_to_old_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        print dir(self.mailer.mail.outbox[0])
        self.fail()
        
