from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.models import Credential
from pdoauth.CredentialManager import CredentialManager
from test.helpers.EmailUtil import EmailUtil
from pdoauth.EmailHandling import EmailHandling
from pdoauth.WebInterface import WebInterface
from test.helpers.FakeInterFace import FakeInterface, FakeApp, FakeMail

exampleBody = "foo"
exampleHtml = "bar"

class EmailChange(EmailHandling, WebInterface):
    def emailChangeInit(self, newEmailAddress, user):
        secret, expiry = CredentialManager.createTemporaryCredential(user, "changeemail")
        self.sendEmail(user, secret, expiry, "PASSWORD_VERIFICATION")
        user.email = newEmailAddress
        self.sendEmail(user, secret, expiry, "PASSWORD_VERIFICATION")

class EmailChangeTest(PDUnitTest, EmailUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials().user
        self.oldEmailAddress = self.userCreationEmail
        self.newEmailAddress = "email{0}@example.com".format(self.randString)
        self.controller = EmailChange(FakeInterface())
        self.controller.app = FakeApp()
        self.controller.mail = FakeMail()

    @test
    def emailChangeInit_creates_a_temporary_credential(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertNotEqual(None, Credential.getByUser(self.user, "changeemail"))

    @test
    def emailChangeInit_send_email_to_old_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertEqual(self.oldEmailAddress,self.controller.mail.outbox[0].recipients[0])

    @test
    def emailChangeInit_send_email_to_new_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertEqual(self.newEmailAddress,self.controller.mail.outbox[1].recipients[0])
        
    @test
    def email_change_init_email_to_old_address_is_formatted_correctly(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        message = self.controller.mail.outbox[0]
        self.assertEqual(message.body,exampleBody);
        self.assertEqual(message.html,exampleHtml);
