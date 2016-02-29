# pylint: disable=line-too-long
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.FakeInterFace import FakeInterface, FakeMail, FakeApp
from pdoauth.EmailHandling import EmailHandling
from pdoauth.models.Credential import Credential

exampleBody = """Dear abc@xyz.uw,
This is a reset email you got with a secret <a href="https://local.sso.edemokraciagep.org:8888/static/login.html?secret=th1s1sth4s3cret">secret</a>, and
you have to send it back until 11 Dec 2098 12:34:56.

Sincerely,
The Test machine
"""

class TestMailer(EmailHandling, FakeInterface):
    app = FakeApp()
    mail = FakeMail()

class EmailTest(PDUnitTest, UserUtil):

    def setUp(self):
        self.mailer = TestMailer()
        cred = self.createUserWithCredentials()
        self.user = cred.user

    @test
    def email_body_is_formatted_correctly(self):
        self.user.email='abc@xyz.uw'
        self.mailer.sendEmail(self.user, 'th1s1sth4s3cret', 4069139696, 'PASSWORD_RESET')
        self.assertEqual(self.mailer.mail.outbox[0]['body'],exampleBody);
        self.user.rm()

    @test
    def password_reset_email_subject_is_PASSWORD_RESET_EMAIL_SUBJECT(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertEqual(self.mailer.mail.outbox[0]['subject'],"password reset");

    @test
    def password_reset_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertTrue("This is a reset email" in self.mailer.mail.outbox[0]['body']);

    @test
    def password_reset_email_body_contains_user(self):
        self.mailer.sendPasswordResetMail(self.user)
        self.assertTrue(self.user.email in self.mailer.mail.outbox[0]['body']);

    @test
    def password_reset_email_body_contains_secret(self):
        self.mailer.sendPasswordResetMail(self.user)
        cred = Credential.getByUser(self.user,"email_for_password_reset")
        body = self.mailer.mail.outbox[0]['body']
        self.assertTrue(cred.secret in body);

    @test
    def password_verification_email_subject_is_PASSWORD_VERIFICATION_EMAIL_SUBJECT(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertEqual(self.mailer.mail.outbox[0]['subject'],"verification");

    @test
    def password_verification_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertTrue("This is a verification email" in self.mailer.mail.outbox[0]['body']);

    @test
    def password_verification_email_body_contains_user(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        self.assertTrue(self.user.email in self.mailer.mail.outbox[0]['body']);

    @test
    def password_verification_email_body_contains_secret(self):
        self.mailer.sendPasswordVerificationEmail(self.user)
        cred = Credential.getByUser(self.user,"emailcheck")
        self.assertTrue(cred.secret in self.mailer.mail.outbox[0]['body']);

    @test
    def deregistration_email_subject_is_DEREGISTRATION_EMAIL_SUBJECT(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertEqual(self.mailer.mail.outbox[0]['subject'],"deregistration email");

    @test
    def deregistration_email_body_is_DEREGISTRATION_EMAIL_BODY(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertTrue("This is a deregistration email" in self.mailer.mail.outbox[0]['body']);

    @test
    def deregistration_email_body_contains_user(self):
        self.mailer.sendDeregisterMail(self.user)
        self.assertTrue(self.user.email in self.mailer.mail.outbox[0]['body']);

    @test
    def deregistration_email_body_contains_secret(self):
        self.mailer.sendDeregisterMail(self.user)
        cred = Credential.getByUser(self.user,"deregister")
        self.assertTrue(cred.secret in self.mailer.mail.outbox[0]['body']);

    def tearDown(self):
        self.mailer.mail.outbox=list()