from test.TestUtil import UserTesting, CSRFMixin
from twatson.unittest_annotations import Fixture, test
import config
from pdoauth.app import app
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from pdoauth.forms import credErr
from pdoauth.models.Assurance import Assurance

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
    def your_credentials_are_deleted_in_deregistration(self):
        with app.test_client() as c:
            self.login(c)
            user = User.getByEmail(self.usercreation_email)
            creds = Credential.getByUser(user)
            self.assertTrue(len(creds) > 0)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            c.post(config.base_url+'/deregister', data=data)
            user = User.getByEmail(self.usercreation_email)
            creds = Credential.getByUser(user)
            self.assertTrue(len(creds) == 0)
            
    @test
    def your_assurances_are_deleted_in_deregistration(self):
        with app.test_client() as c:
            self.login(c)
            user = User.getByEmail(self.usercreation_email)
            Assurance.new(user, "test", user)
            assurances = Assurance.getByUser(user)
            self.assertTrue(len(assurances) > 0)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            c.post(config.base_url+'/deregister', data=data)
            user = User.getByEmail(self.usercreation_email)
            assurances = Assurance.getByUser(user)
            self.assertTrue(len(assurances) == 0)

    @test
    def your_user_is_deleted_in_deregistration(self):
        with app.test_client() as c:
            self.login(c)
            user = User.getByEmail(self.usercreation_email)
            self.assertTrue(user is not None)
            data = dict(
                csrf_token = self.getCSRF(c),
                credentialType= "password",
                identifier= self.usercreation_userid,
                secret = self.usercreation_password
            )
            c.post(config.base_url+'/deregister', data=data)
            user = User.getByEmail(self.usercreation_email)
            self.assertTrue(user is None)

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
            self.assertEqual('{{"errors": [{0}]}}'.format(credErr), self.getResponseText(resp))

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
            self.assertEqual('{{"errors": [{0}]}}'.format(credErr), self.getResponseText(resp))

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
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

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
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

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
