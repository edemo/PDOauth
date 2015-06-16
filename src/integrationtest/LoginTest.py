from integrationtest import config
from pdoauth.app import app
from pdoauth.forms import credErr
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class LoginTest(IntegrationTest, UserTesting):

    @test
    def login_does_not_accept_get(self):
        with app.test_client() as client:
            resp = client.get("/v1/login")
            self.assertEquals(resp.status_code, 404)

    @test
    def password_login_needs_identifier(self):
        with app.test_client() as client:
            data = dict(secret=self.mkRandomPassword())
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))

    @test
    def password_login_needs_secret(self):
        with app.test_client() as client:
            data = dict(credentialType=self.mkRandomPassword(), identifier="userid")
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertEqual('{{"errors": ["secret: Field must be at least 8 characters long.", "secret: password should contain lowercase", "secret: password should contain uppercase", "secret: password should contain digit", {0}]}}'.format(credErr),
                text)

    @test
    def password_login_should_send_hidden_field_credentialType(self):
        with app.test_client() as client:
            data = dict(identifier="userid", secret=self.mkRandomPassword())
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["credentialType: '))

    @test
    def password_login_needs_correct_identifier_and_secret(self):
        with app.test_client() as client:
            data = dict(identifier="userid", secret=self.mkRandomPassword(), credentialType='password')
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertEquals(text,'{"errors": ["Bad username or password"]}')

    @test
    def password_login_needs_correct_credentialType(self):
        with app.test_client() as client:
            data = dict(identifier="userid", secret=self.mkRandomPassword(), credentialType='incorrect')
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            expected = '{{"errors": [{0}]}}'.format(credErr)
            self.assertEquals(text,expected)

    @test
    def password_login_works_with_correct_identifier_and_secret(self):
        user = self.createUserWithCredentials().user
        user.activate()
        with app.test_client() as client:
            data = dict(identifier=self.userCreationUserid, secret=self.usercreationPassword, credentialType='password')
            resp = client.post(config.BASE_URL + '/login', data=data)
            self.assertUserResponse(resp)

    @test
    def user_can_authenticate_on_login_page(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertEqual(200, resp.status_code)
            self.assertUserResponse(resp)

    @test
    def login_sets_the_csrf_cookie(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))

    @test
    def inactive_user_cannot_authenticate(self):
        with app.test_client() as client:
            resp = self.login(client, activate=False)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertEquals(text,'{"errors": ["Inactive or disabled user"]}')

    @test
    def authentication_with_bad_userid_is_rejected(self):
        self.createUserWithCredentials()
        data = {
                'credentialType': 'password',
                'identifier': 'baduser',
                'secret': self.usercreationPassword,
        }
        with app.test_client() as client:
            resp = client.post(config.BASE_URL + '/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertTrue("Bad username or password" in text)

    @test
    def authentication_with_bad_secret_is_rejected(self):
        self.createUserWithCredentials()
        data = {
                'credentialType': 'password',
                'identifier': self.userCreationUserid,
                'secret': self.mkRandomPassword(),
        }
        with app.test_client() as client:
            resp = client.post(config.BASE_URL + '/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertEqual('{"errors": ["Bad username or password"]}', text)
