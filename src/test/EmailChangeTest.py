from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.models import Credential
from test.helpers.EmailUtil import EmailUtil
import time
from uuid import uuid4
from pdoauth.models.User import User
from pdoauth.ReportedError import ReportedError
from pdoauth.Messages import badChangeEmailSecret
from pdoauth.models.Assurance import Assurance

class EmailChangeTest(PDUnitTest, EmailUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials().user
        Assurance.new(self.user, 'emailverification', self.user)
        self.oldEmailAddress = self.userCreationEmail
        self.newEmailAddress = "email{0}@example.com".format(self.mkRandomString(5))
        PDUnitTest.setUp(self)

    @test
    def emailChangeInit_creates_a_temporary_credential(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertNotEqual(None, Credential.getByUser(self.user, "changeemail"))

    @test
    def changeemail_credential_contains_new_emailaddress(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertEqual(self.newEmailAddress, Credential.getByUser(self.user, "changeemail").getAdditionalInfo())
        
    @test
    def emailChangeInit_sends_email_to_old_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertEqual(self.oldEmailAddress,self.controller.mail.outbox[0].recipients[0])

    @test
    def emailChangeInit_sends_email_to_new_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertEqual(self.newEmailAddress,self.controller.mail.outbox[1].recipients[0])
        
    @test
    def emailChangeInit_email_to_old_address_is_formatted_correctly(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        message = self.controller.mail.outbox[0]
        self.assertTrue(message.body.startswith("oldDear "))
        self.assertIn(self.user.email, message.body)
        self.assertTrue(message.html.startswith("oldhtml "))
        self.assertIn(self.user.email, message.html)
        self.assertIn(self.oldEmailAddress, message.body)
        self.assertIn(self.newEmailAddress, message.body)


    @test
    def emailChangeInit_email_to_new_address_is_formatted_correctly(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        message = self.controller.mail.outbox[1]
        self.assertTrue(message.body.startswith("newDear "))
        self.assertIn(self.user.email, message.body)
        self.assertTrue(message.html.startswith("newhtml "))
        self.assertIn(self.user.email, message.html)
        self.assertIn(self.oldEmailAddress, message.body)
        self.assertIn(self.newEmailAddress, message.body)

    @test
    def emailChangeInit_does_not_change_email_address(self):
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        user = User.get(self.user.userid)
        self.assertEqual(self.oldEmailAddress, self.user.email)
        self.assertEqual(self.oldEmailAddress, user.email)

    @test
    def emailChangeInit_clears_timed_out_changeemail_credentials(self):
        for someone in User.query.all()[:5]:  # @UndefinedVariable
            Credential.new(someone, 'changeemail', unicode(time.time()-1)+":"+unicode(uuid4()), unicode(uuid4()))
        self.assertTrue(self.countExpiredCreds('changeemail')>=5)
        self.controller.emailChangeInit(self.newEmailAddress, self.user)
        self.assertTrue(self.countExpiredCreds('changeemail')==0)

    @test
    def confirmChangeEmail_throws_403_bad_secret_for_email_change_if_secret_is_not_correct(self):
        with self.assertRaises(ReportedError) as context:
            self.doConfirmChangeEmail(secret="badSecret")
        self.assertEqual(context.exception.status,403)
        self.assertEqual(context.exception.descriptor,badChangeEmailSecret)

    @test
    def confirmChangeEmail_changes_email_address_to_the_new_one(self):
        self.doConfirmChangeEmail()
        user = User.get(self.user.userid)
        self.assertEqual(self.newEmailAddress, user.email)

    @test
    def confirmChangeEmail_does_not_change_email_address_to_the_new_one_if_confirm_is_false(self):
        self.doConfirmChangeEmail(confirm=False)
        user = User.get(self.user.userid)
        self.assertEqual(self.oldEmailAddress, user.email)

    @test
    def confirmChangeEmail_deletes_changeemail_credential(self):
        self.doConfirmChangeEmail()
        self.assertEqual(None,Credential.getByUser(self.user, 'changeemail'))

    @test
    def confirmChangeEmail_deletes_emailverification_assurance(self):
        self.doConfirmChangeEmail()
        self.assertEqual(list(),Assurance.listByUser(self.user,'emailverification'))

    @test
    def confirmChangeEmail_deletes_changeemail_credential_even_when_confirm_is_false(self):
        self.doConfirmChangeEmail(confirm=False)
        self.assertEqual(None,Credential.getByUser(self.user, 'changeemail'))

    @test
    def confirmChangeEmail_sends_an_email_to_the_new_address_with_a_security_warning(self):
        self.doConfirmChangeEmail()
        message = self.controller.mail.outbox[2]
        self.assertEqual(self.oldEmailAddress,self.controller.mail.outbox[0].recipients[0])
        self.assertTrue(message.body.startswith("warnDear "))
        self.assertIn(self.user.email, message.body)
        self.assertTrue(message.html.startswith("warnhtml "))
        self.assertIn(self.user.email, message.html)

    @test
    def confirmChangeEmail_starts_an_emailverification_for_the_new_address(self):
        self.doConfirmChangeEmail()
        self.assertEqual(self.user,Credential.getByUser(self.user, 'emailcheck').user)
