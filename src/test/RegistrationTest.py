from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.app import app
import pdoauth.main  # @UnusedImport
from flask_login import logout_user

class RegistrationTest(Fixture, UserTesting):

    def setUp(self):
        self.setupRandom()
 
    @test
    def register_and_get_our_info(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)
            logout_user()
            self.assertUserResponse(resp)
            self.assertEquals(outbox[0].subject,"verification")
            self.assertEquals(outbox[0].sender,"test@edemokraciagep.org")
            data = {
                'username': "id_{0}".format(self.randString), 
                'password':"password_{0}".format(self.randString+self.randString), 
                'next':'/v1/users/me'
            }
            resp = c.post('http://localhost.local/login', data=data)
            self.assertUserResponse(resp)
            
            resp = c.get('http://localhost.local/v1/users/me')
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
        with app.test_client() as c:
            resp, outbox  = self.register(c, email=email)  # @UnusedVariable
            logout_user()
            self.assertEquals(400, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["There is already a user with that username or email", "'))

    @test
    def registration_is_impossible_without_email(self):
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.randString),
            }
            resp = c.post('https://localhost.local/v1/register', data=data)
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
            resp = c.post('https://localhost.local/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["secret: '))

    @test
    def registration_should_give_a_credential_type(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.randString),
                'email': email,
            }
            resp = c.post('https://localhost.local/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["credentialType: '))

    @test
    def registration_should_give_an_identifier(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'credentialType':'password', 
                'secret':"password_{0}".format(self.randString),
                'email': email,
            }
            resp = c.post('https://localhost.local/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))

    @test
    def password_registration_is_impossible_with_already_used_username(self):
        email = "k0-{0}@example.com".format(self.randString)
        with app.test_client() as c:
            data = {
                'identifier': "id_{0}".format(self.randString), 
                'credentialType':'password', 
                'secret':"password_{0}".format(self.randString),
                'email': email,
            }
            resp = c.post('https://localhost.local/v1/register', data=data)
            self.assertEquals(resp.status_code, 200)
            data['email'] = "k1-{0}@example.com".format(self.randString)
            resp = c.post('https://localhost.local/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["There is already a user with that username or email", "'))
