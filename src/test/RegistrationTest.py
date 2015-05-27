from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.app import app
from flask_login import logout_user
import config
from pdoauth.models.Assurance import Assurance, emailVerification
import time
from pdoauth.models.User import User
import re

class RegistrationTest(Fixture, UserTesting):

    def setUp(self):
        self.setupRandom()
 
    @test
    def you_can_register_with_username__password__email_and_hash(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            self.assertUserResponse(resp)

    @test
    def on_registration_a_temporary_email_verification_credential_is_registered(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            data = self.fromJson(resp)
            self.assertEquals("emailcheck", data['credentials'][1]['credentialType'])
    @test
    def the_emailcheck_secret_is_not_shown_in_the_registration_answer(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            text = self.getResponseText(resp)
            secret=re.search('href=".*verify_email/([^"]*)"',outbox[0].body).group(1)
            self.assertTrue(not (secret in text))

    @test
    def you_can_register_without_hash(self):
        with app.test_client() as c:
            email = "{0}@example.com".format(self.randString)
            self.registered_email = email
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': email,
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertUserResponse(resp)

    @test
    def if_you_register_without_hash_it_will_be_null(self):
        with app.test_client() as c:
            email = "{0}@example.com".format(self.randString)
            self.registered_email = email
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': email,
            }
            c.post(config.base_url + '/v1/register', data=data)
            user = User.getByEmail(email)
            self.assertEqual(user.hash, None)

    @test
    def you_can_login_after_registration(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)
            logout_user()
            self.assertUserResponse(resp)
            self.assertEquals(outbox[0].subject,"verification")
            self.assertEquals(outbox[0].sender,"test@edemokraciagep.org")
            data = {
                'credentialType': 'password',
                'identifier': "id_{0}".format(self.randString), 
                'secret': self.registered_password
            }
            resp = c.post(config.base_url + '/login', data=data)
            self.assertUserResponse(resp)
            
            resp = c.get(config.base_url + '/v1/users/me')
            self.assertEquals(resp.status_code, 200)
            data = self.fromJson(resp)
            self.assertTrue(data.has_key('userid'))
            self.assertTrue(u'@example.com' in data['email'])

    @test
    def user_cannot_register_twice_with_same_email(self):
        email = "k-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            resp , outbox = self.register(c,email=email)  # @UnusedVariable
            logout_user()
            self.assertUserResponse(resp)
        self.setupRandom()
        with app.test_client() as c:
            resp, outbox  = self.register(c, email=email)  # @UnusedVariable
            logout_user()
            self.assertEquals(400, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["email: There is already a user with that email'))

    @test
    def registration_is_impossible_without_email(self):
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEquals(self.getResponseText(resp),'{"errors": ["email: Invalid email address."]}')

    @test
    def password_registration_needs_good_password(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"1234",
                'email': email,
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["secret: '))

    @test
    def registration_should_give_a_credential_type(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': email,
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["credentialType: '))

    @test
    def registration_should_give_an_identifier(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': email,
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))

    @test
    def password_registration_is_impossible_with_already_used_username(self):
        self.setupRandom()
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'identifier': "id_{0}".format(self.randString), 
                'credentialType':'password', 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': email,
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 200)
            data['email'] = "k1-{0}@example.com".format(self.randString)
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: There is already a user with that username'))

    @test
    def When_a_hash_is_registered_which_is_already_used_by_another_user___the_user_is_notified_about_the_fact(self):
        anotherUser = self.createUserWithCredentials()
        self.setupRandom()
        theHash = self.createHash()
        anotherUser.hash = theHash
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': "email{0}@example.com".format(self.randString),
                'digest': theHash
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEqual(200, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue("another user is using your hash" in text)

    @test
    def When_a_hash_is_registered_which_is_already_used_by_another_assured_user___the_user_is_notified_about_the_fact_and_registration_fails(self):
        anotherUser = self.createUserWithCredentials()
        Assurance.new(anotherUser, "test", anotherUser, time.time())
        self.setupRandom()
        theHash = self.createHash()
        anotherUser.hash = theHash
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': "email{0}@example.com".format(self.randString),
                'digest': theHash
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEqual(400, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue("another user is using your hash" in text)

    @test
    def the_emailverification_assurance_does_not_count_in_hash_collision(self):
        anotherUser = self.createUserWithCredentials()
        Assurance.new(anotherUser, emailVerification, anotherUser, time.time())
        self.setupRandom()
        theHash = self.createHash()
        anotherUser.hash = theHash
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.mkRandomPassword()),
                'email': "email{0}@example.com".format(self.randString),
                'digest': theHash
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            self.assertEqual(200, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue("another user is using your hash" in text)
