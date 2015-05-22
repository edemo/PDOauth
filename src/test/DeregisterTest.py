from test.TestUtil import UserTesting, CSRFMixin
from twatson.unittest_annotations import Fixture, test
import config
from pdoauth.app import app
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential

class DeregisterTest(Fixture, UserTesting, CSRFMixin):

    @test
    def you_can_deregister_with_your_login_credentials_and_csrf(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 200)
            self.assertEqual('{"message": "deregistered"}', self.getResponseText(resp))

    @test
    def you_have_to_use_the_credentials_used_for_login_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            user = User.getByEmail(self.usercreation_email)
            self.setupUserCreationData()
            Credential.new(user, "password", self.usercreation_userid, self.usercreation_password)
            data = dict(
                csrf_token= self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["You should use your login credentials to deregister"]}', self.getResponseText(resp))

    @test
    def you_need_credentialType_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["credentialType: Invalid value, must be one of: password, facebook."]}', self.getResponseText(resp))

    @test
    def you_need_valid_credentialType_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "invalid",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["credentialType: Invalid value, must be one of: password, facebook."]}', self.getResponseText(resp))

    @test
    def you_need_identifier_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 25 characters long."]}', self.getResponseText(resp))

    @test
    def you_need_valid_identifier_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= "inv",
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 25 characters long."]}', self.getResponseText(resp))

    @test
    def you_need_secret_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long.", "secret: password should contain lowercase", "secret: password should contain uppercase", "secret: password should contain digit"]}'
, self.getResponseText(resp))

    @test
    def you_need_valid_secret_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = "l"
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long.", "secret: password should contain uppercase", "secret: password should contain digit"]}'
, self.getResponseText(resp))

    @test
    def you_need_csrf_token_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}', self.getResponseText(resp))

    @test
    def you_need_valid_csrf_token_to_deregister(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                csrf_token= "invalid",
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            resp = c.post(config.base_url+'/deregister', data=data)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}', self.getResponseText(resp))
