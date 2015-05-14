from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.app import app, mail
from bs4 import BeautifulSoup
import re
from pdoauth.models.Credential import Credential
import time
from uuid import uuid4
from pdoauth.models.User import User
from pdoauth.CredentialManager import CredentialManager

class PasswordResetTest(Fixture, UserTesting):

    def setUp(self):
        self.createUserWithCredentials()

    @test
    def have_passwordreset_uri(self):
        with app.test_client() as c:
            resp = c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
            self.assertEqual(resp.status_code, 200)

    @test
    def password_reset_success_message(self):
        with app.test_client() as c:
            resp = c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
            data = self.fromJson(resp)
            self.assertEqual(data['message'],"Password reset email has successfully sent.")

    @test
    def password_reset_email_is_sent(self):
        with app.test_client() as c:
            with mail.record_messages() as outbox:
                c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
                self.assertEqual(outbox[0].subject, "Password Reset for {0}".format(app.config.get('SERVER_NAME')))

    def the_reset_link_is_in_the_reset_email(self):
        with app.test_client() as c:
            with mail.record_messages() as outbox:
                c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
                text = outbox[0].body
                soup = BeautifulSoup(text)
                passwordResetLink = soup.find("a")['href']
        return passwordResetLink

    @test
    def password_reset_email_contains_a_password_reset_link(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        self.assertTrue(passwordResetLink is not None)

    @test
    def password_reset_link_is_of_correct_form(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        self.assertTrue(re.match("https://.*?secret=[^&]*$",passwordResetLink))

    @test
    def password_reset_link_contains_correct_secret(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        secret = passwordResetLink.split('?secret=')[1]
        cred = Credential.get('email_for_password_reset',secret)
        self.assertEquals(cred.identifier, secret)

    @test
    def password_reset_credential_have_4_hours_expiration_time(self):
        now = time.time()
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        secret = passwordResetLink.split('?secret=')[1]
        cred = Credential.get('email_for_password_reset',secret)
        expiry = float(cred.secret) - now
        self.assertTrue(expiry > 14395 and expiry < 14405)
        
    @test
    def password_reset_for_invalid_email_fails(self):
        with app.test_client() as c:
            resp = c.get("/v1/users/{0}/passwordreset".format("invalid@email.com"))
            self.assertEqual(resp.status_code, 400)

    @test
    def invalid_email_response_have_correct_message(self):
        with app.test_client() as c:
            resp = c.get("/v1/users/{0}/passwordreset".format("invalid@email.com"))
            data = self.fromJson(resp)
            self.assertEqual(data['errors'][0],'Invalid email address')

    @test
    def password_reset_link_leads_to_password_reset_form(self):
        passwordResetLink = self.the_reset_link_is_in_the_reset_email()
        with app.test_client() as c:
            resp = c.get(passwordResetLink)
            self.assertEqual(resp.status_code, 200)

    @test
    def password_reset_needs_password(self):
        secret = unicode(uuid4())
        with app.test_client() as c:
            data = dict(secret=secret)
            resp = c.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 400)
            respData = self.fromJson(resp)
            self.assertTrue("password" in respData['errors'][0])

    @test
    def password_reset_needs_secret(self):
        password = unicode(uuid4())
        with app.test_client() as c:
            data = dict(password=password)
            resp = c.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 400)
            respData = self.fromJson(resp)
            self.assertTrue("secret" in respData['errors'][0])

    @test
    def password_reset_secret_have_to_be_valid(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            resp = c.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 404)
            respData = self.fromJson(resp)
            self.assertEquals("What?",respData['errors'][0])

    @test
    def Valid_secret_is_accepted(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        user = User.getByEmail(self.usercreation_email)
        Credential.new(user, 'email_for_password_reset', secret, time.time()+3600)
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            resp = c.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 200)
            respData = self.fromJson(resp)
            self.assertEquals("Password successfully changed",respData['message'])

    @test
    def successful_password_reset_sets_the_password(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        user = User.getByEmail(self.usercreation_email)
        Credential.new(user, 'email_for_password_reset', secret, time.time()+3600)
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            c.post("/v1/password_reset", data = data)
            cred = Credential.getByUser(user, "password")
            self.assertEquals(cred.secret, CredentialManager.protect_secret(password))

    @test
    def successful_password_clears_the_temporary_credential(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        user = User.getByEmail(self.usercreation_email)
        Credential.new(user, 'email_for_password_reset', secret, time.time()+3600)
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            c.post("/v1/password_reset", data = data)
            newcred = Credential.get('email_for_password_reset', secret)
            self.assertEquals(newcred, None)

    @test
    def no_password_reset_for_timed_out_temporary_credential(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        user = User.getByEmail(self.usercreation_email)
        Credential.new(user, 'email_for_password_reset', secret, time.time()-1)
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            resp = c.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 404)

    @test
    def bad_secret_clears_up_all_timed_out_temporary_credentials(self):
        password = unicode(uuid4())
        secret = unicode(uuid4())
        for someone in User.query.all()[:5]:  # @UndefinedVariable
            Credential.new(someone, 'email_for_password_reset', unicode(uuid4()), time.time()-1)
        with app.test_client() as c:
            data = dict(password=password, secret=secret)
            c.post("/v1/password_reset", data = data)
            expiredcreds = []
            now = time.time()
            creds = Credential.query.filter_by(credentialType='email_for_password_reset')  # @UndefinedVariable
            for c in creds:
                if (float(c.secret) < now):
                    expiredcreds.append(c)
            self.assertEqual(expiredcreds,[])
