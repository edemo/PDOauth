from integrationtest import config
from pdoauth.app import app
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest

class LoginIntegrationTest(IntegrationTest, UserTesting):

    
    def test_login_does_not_accept_get(self):
        with app.test_client() as client:
            resp = client.get("/v1/login")
            self.assertEqual(resp.status_code, 404)

    
    def test_password_login_needs_identifier(self):
        with app.test_client() as client:
            data = dict(password=self.mkRandomPassword(), credentialType='password')
            resp = client.post(config.BASE_URL + '/v1/login', data=data)
            self.assertEqual(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["identifier: '))

    
    def test_password_login_needs_secret(self):
        with app.test_client() as client:
            data = dict(credentialType="password", identifier="userid")
            resp = client.post(config.BASE_URL + '/v1/login', data=data)
            self.assertEqual(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue("password: Field must be at least 8 characters long." in  text)

    
    def test_password_login_needs_correct_identifier_and_secret(self):
        with app.test_client() as client:
            data = dict(identifier="userid", password=self.mkRandomPassword(), credentialType='password')
            resp = client.post(config.BASE_URL + '/v1/login', data=data)
            self.assertEqual(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertEqual(text,'{"errors": ["Bad username or password"]}')

    
    def test_password_login_needs_correct_credentialType(self):
        with app.test_client() as client:
            data = dict(identifier="userid", password=self.mkRandomPassword(), credentialType='incorrect')
            resp = client.post(config.BASE_URL + '/v1/login', data=data)
            self.assertEqual(resp.status_code, 403)
            self.assertCredentialErrorresponse(resp)

    
    def test_user_can_authenticate_on_login_page(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertEqual(200, resp.status_code)
            self.assertUserResponse(resp)

    
    def test_you_have_to_be_logged_in_to_log_out(self):
        with app.test_client() as client:
            resp = client.get("/v1/logout")
            self.assertEqual(resp.status_code, 403)

