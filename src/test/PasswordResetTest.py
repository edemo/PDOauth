#pylint: disable=no-member
from test.helpers.PDUnitTest import PDUnitTest
import re
from pdoauth.models.Credential import Credential
import time
from test.helpers.FakeInterFace import FakeForm
from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.User import User
from uuid import uuid4
from pdoauth.ReportedError import ReportedError
from test.helpers.EmailUtil import EmailUtil

class PasswordResetTest(PDUnitTest, EmailUtil):

    
    def test_password_reset_email_is_sent_to_valid_email(self):
        self._sendPasswordResetEmail()
        self.assertEqual(len(self.outbox), 1)

    
    def test_password_reset_email_send_returns_success_message(self):
        status = self._sendPasswordResetEmail()
        self.assertEqual(status,200)
        self.assertEqual(self.data['message'],"Password reset email has been successfully sent.")

    
    def test_the_reset_link_is_in_the_reset_email_in_correct_form(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        self.assertTrue(re.match("https://.*?secret=[^&]*$",passwordResetLink))

    
    def test_password_reset_link_contains_correct_secret(self):
        self.the_reset_link_is_in_the_reset_email()
        self.assertEqual(self.tempcred.secret, self.secret)

    
    def test_password_reset_credential_have_4_hours_expiration_time(self):
        now = time.time()
        self.the_reset_link_is_in_the_reset_email()
        expiry = self.tempcred.getExpirationTime() - now
        self.assertTrue(expiry > 14395 and expiry < 14405)

    
    def test_password_reset_email_send_for_invalid_email_fails(self):
        self.assertReportedError(self._sendPasswordResetEmail, ["invalid@email.com"],
                400, ['Invalid email address',"invalid@email.com"])

    
    def test_successful_password_reset_sets_the_password(self):
        self.doPasswordReset()
        self.assertEqual(self.cred.secret, CredentialManager.protect_secret(self.newPassword))


    def createPasswordResetFormWithSecret(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        self.secret = passwordResetLink.split('secret=')[1]
        self.setupRandom()
        self.newPassword = self.mkRandomPassword()
        data = dict(password=self.newPassword, secret=self.secret)
        form = FakeForm(data)
        return form

    def doPasswordReset(self):
        form = self.createPasswordResetFormWithSecret()
        self.controller.doPasswordReset(form)
        self.user = User.getByEmail(self.userCreationEmail)
        self.cred = Credential.getByUser(self.user, "password")

    
    def test_reusing_password_reset_secret_gives_error(self):
        form = self.createPasswordResetFormWithSecret()
        self.controller.doPasswordReset(form)
        with self.assertRaises(ReportedError) as context:
            self.controller.doPasswordReset(form)
        self.assertEqual(context.exception.status,404)

    
    def test_password_reset_creates_password_if_it_does_not_exists(self):
        form = self.createPasswordResetFormWithSecret()
        user = User.getByEmail(self.userCreationEmail)
        passcred = Credential.getByUser(user, "password")
        passcred.rm()
        self.controller.doPasswordReset(form)
        newPassCred = Credential.getByUser(user, "password")
        self.assertEqual(newPassCred.secret, CredentialManager.protect_secret(self.newPassword))

    
    def test_successful_password_clears_the_temporary_credential(self):
        form = self.createPasswordResetFormWithSecret()
        self.controller.doPasswordReset(form)
        self.assertEqual(Credential.get('email_for_password_reset', self.secret), None)

    
    def test_no_password_reset_for_timed_out_temporary_credential(self):
        form = self.createPasswordResetFormWithSecret()
        self.tempcred.identifier = str(time.time() -1)
        self.assertReportedError(self.controller.doPasswordReset,(form,),
                404, ['The secret has expired'])


    
    def test_bad_secret_clears_up_all_timed_out_temporary_credentials(self):
        password = self.mkRandomPassword()
        secret = uuid4().hex
        for someone in User.query.all()[:5]:  # @UndefinedVariable
            Credential.new(someone, 'email_for_password_reset', str(time.time()-1)+":"+uuid4().hex, uuid4().hex)
        self.assertTrue(self.countExpiredCreds()>=5)
        data = dict(password=password, secret=secret)
        self.assertReportedError(self.controller.doPasswordReset,(FakeForm(data),),
                404, ['The secret has expired'])
        self.assertEqual(self.countExpiredCreds(),0)
