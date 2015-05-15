from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
import config
from pdoauth.app import app

class LoginTest(Fixture, UserTesting):

    @test
    def login_does_not_accept_get(self):
        with app.test_client() as c:
            resp = c.get("/v1/login")
            self.assertEquals(resp.status_code, 404)

    @test
    def password_login_needs_username(self):
        with app.test_client() as c:
            data = dict(password="password")
            resp = c.post(config.base_url + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["username: '))

    @test
    def password_login_needs_password(self):
        with app.test_client() as c:
            data = dict(username="userid")
            resp = c.post(config.base_url + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["password: '))

    @test
    def password_login_should_send_hidden_field_credentialType(self):
        with app.test_client() as c:
            data = dict(username="userid", password="password")
            resp = c.post(config.base_url + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": ["credentialType: '))

    @test
    def password_login_needs_correct_username_and_password(self):
        with app.test_client() as c:
            data = dict(username="userid", password="password", credentialType='password')
            resp = c.post(config.base_url + '/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertEquals(text,'{"errors": ["Bad username or password"]}')

    @test
    def password_login_works_with_correct_username_and_password(self):
        user = self.createUserWithCredentials()
        user.activate()
        with app.test_client() as c:
            data = dict(username=self.usercreation_userid, password=self.usercreation_password, credentialType='password')
            resp = c.post(config.base_url + '/login', data=data)
            self.assertUserResponse(resp)

    @test
    def User_can_authenticate_on_login_page(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertEqual(200, resp.status_code)
            self.assertUserResponse(resp)

    @test
    def login_sets_the_csrf_cookie(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))

    @test
    def inactive_user_cannot_authenticate(self):
        with app.test_client() as c:
            resp = self.login(c, activate=False)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertEquals(text,'{"errors": ["Inactive or disabled user"]}')

    @test
    def Authentication_with_bad_userid_is_rejected(self):
        self.createUserWithCredentials()
        data = {
                'credentialType': 'password',
                'username': 'baduser',
                'password': self.usercreation_password,
                'next': '/foo'
        }
        with app.test_client() as c:
            resp = c.post(config.base_url + '/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertTrue("Bad username or password" in text)

    @test
    def Authentication_with_bad_password_is_rejected(self):
        self.createUserWithCredentials()
        data = {
                'credentialType': 'password',
                'username': self.usercreation_userid,
                'password': 'badpassword',
                'next': '/foo'
        }
        with app.test_client() as c:
            resp = c.post(config.base_url + '/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertTrue("Bad username or password" in text)
