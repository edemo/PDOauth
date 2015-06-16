from pdoauth.app import app
from flask_login import logout_user
from integrationtest import config
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class RegistrationIntegrationTest(IntegrationTest, UserTesting):

    def setUp(self):
        self.setupRandom()
 
    @test
    def you_can_register_with_username__password__email_and_hash(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            self.assertUserResponse(resp)

    @test
    def registration_sets_the_csrf_cookie(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))


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
            data = self.prepareData()
            data.pop('email')
            resp = c.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEquals(self.getResponseText(resp),'{"errors": ["email: Invalid email address."]}')

    @test
    def password_registration_needs_good_password(self):
        data = self.prepareData()
        data['secret'] = '1234'
        with app.test_client() as c:
            resp = c.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["secret: '))

    @test
    def registration_should_give_a_credential_type(self):
        data = self.prepareData()
        data.pop('credentialType')
        with app.test_client() as c:
            resp = c.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["credentialType: '))

    @test
    def registration_should_give_an_identifier(self):
        data = self.prepareData()
        data.pop('identifier')
        with app.test_client() as c:
            resp = c.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))
