from pdoauth.app import app
from flask_login import logout_user
from integrationtest import config
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from test.helpers.CryptoTestUtil import SPKAC

class RegistrationIntegrationTest(IntegrationTest, UserTesting):

    def setUp(self):
        self.setupRandom()

    @test
    def you_can_register_with_username__password__email_and_hash(self):
        with app.test_client() as client:
            resp = self.register(client)
            self.assertUserResponse(resp)

    @test
    def user_cannot_register_twice_with_same_email(self):
        email = "k-{0}@example.com".format(self.randString)
        with app.test_client() as client:
            self.register(client,email=email)
            logout_user()
            self.setupRandom()
            resp = self.register(client, email=email)
            self.assertEquals(400, resp.status_code)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["email: There is already a user with that email'))

    @test
    def registration_is_impossible_without_email(self):
        with app.test_client() as client:
            data = self.prepareAuthInterfaceData()
            data.pop('email')
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEquals(self.getResponseText(resp),'{"errors": ["email: Invalid email address."]}')

    @test
    def password_registration_needs_good_password(self):
        data = self.prepareAuthInterfaceData()
        data['secret'] = '1234'
        with app.test_client() as client:
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["secret: '))

    @test
    def registration_should_give_a_credential_type(self):
        data = self.prepareAuthInterfaceData()
        data.pop('credentialType')
        with app.test_client() as client:
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertTrue(self.getResponseText(resp).startswith('{"errors": ["credentialType: '))

    @test
    def registration_should_give_an_identifier(self):
        data = self.prepareAuthInterfaceData()
        data.pop('identifier')
        with app.test_client() as client:
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.assertEquals(resp.status_code, 400)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))

    @test
    def you_can_give_a_hash_with_ssl_registration(self):
        self.setupUserCreationData()
        with app.test_client() as client:
            data = dict(email=self.userCreationEmail, pubkey=SPKAC)
            theHash = self.createHash()
            data["digest"]= theHash
            resp = client.post(config.BASE_URL + '/v1/keygen', data=data)
            self.assertEqual(resp.status_code, 200)
            resp = client.get(config.BASE_URL + '/v1/users/me')
            respData = resp.data
            self.assertTrue(self.userCreationEmail in respData)
            self.assertTrue(theHash in respData)
