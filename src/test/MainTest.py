# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Application import Application
from pdoauth import main  # @UnusedImport
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
import json
from test.TestUtil import UserTesting, CSRFMixin, ServerSide
from flask_login import logout_user, current_user
import re
from pdoauth.models.Assurance import Assurance
import time

app.extensions["mail"].suppress = True

class MainTest(Fixture, CSRFMixin, UserTesting, ServerSide):

    def setUp(self):
        self.setupRandom()
        self.app = app.test_client()

    @test
    def NoRootUri(self):
        resp = self.app.get("/")
        self.assertEquals(resp.status_code, 404,)

    @test
    def Unauthenticated_user_is_redirected_to_login_page_when_tries_to_do_oauth_with_us(self):
        redirectUri = 'https://client.example.com/oauth/redirect'
        appid = "app2-{0}".format(self.randString)
        self.appsecret = "secret2-{0}".format(self.randString)
        Application.new(appid, self.appsecret, redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect".format(appid)
        resp = self.app.get(uri)
        self.assertEquals(302,resp.status_code)
        self.assertTrue(resp.headers.has_key('Content-Length'))
        self.assertTrue(resp.headers['Location'].startswith("http://localhost.local/login"))

    @test
    def User_can_authenticate_on_login_page(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertEqual(200, resp.status_code)
            self.assertUserResponse(resp)

    @test
    def inactive_user_cannot_authenticate(self):
        with app.test_client() as c:
            resp = self.login(c, activate=False)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertEquals(text,'{"errors": "Inactive or disabled user"}')

    @test
    def Authentication_with_bad_userid_is_rejected(self):
        self.create_user_with_credentials()
        data = {
                'username': 'baduser',
                'password': self.usercreation_password,
                'next': '/foo'
        }
        with app.test_client() as c:
            resp = c.post('http://localhost.local/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertTrue("Bad username or password" in text)

    @test
    def Authentication_with_bad_password_is_rejected(self):
        self.create_user_with_credentials()
        data = {
                'username': self.usercreation_userid,
                'password': 'badpassword',
                'next': '/foo'
        }
        with app.test_client() as c:
            resp = c.post('http://localhost.local/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(403, resp.status_code)
            self.assertTrue("Bad username or password" in text)


    @test
    def authorization_code_can_be_obtained_by_an_authenticated_user_using_correct_client_id_and_redirect_uri(self):
        self.loginAndGetCode()

    @test
    def server_side_request(self):
        code = self.loginAndGetCode()
        self.doServerSideRequest(code)

    @test
    def get_user_info(self):
        code = self.loginAndGetCode()
        data = self.doServerSideRequest(code)
        with app.test_client() as serverside:
            resp = serverside.get("https://localhost.local/v1/users/me", headers=[('Authorization', '{0} {1}'.format(data['token_type'], data['access_token']))])
            self.assertEquals(resp.status_code, 200)
            data = json.loads(self.getResponseText(resp))
            self.assertTrue(data.has_key('userid'))


    @test
    def logged_in_user_can_get_its_info(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('userid'))

    @test
    def user_info_contains_assurance(self):
        with app.test_client() as c:
            self.login(c)
            myEmail = current_user.email
            now = time.time()
            Assurance.new(current_user, 'test', current_user, now)
            Assurance.new(current_user, 'test2', current_user, now)
            Assurance.new(current_user, 'test2', current_user, now)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('assurances'))
            assurances = data['assurances']
            assurance = assurances['test'][0]
            self.assertEqual(assurance['assurer'], myEmail)
            self.assertEqual(assurance['user'], myEmail)
            self.assertEqual(assurance['timestamp'], now)
            self.assertEqual(assurance['readable_time'], time.asctime(time.gmtime(now)))
            self.assertEqual(len(assurances['test2']),2)

    @test
    def email_validation_gives_emailverification_assurance(self):
        with app.test_client() as c:
            resp, outbox = self.register(c)
            email = self.registered_email
            logout_user()
            self.assertUserResponse(resp)
            self.validateUri=re.search('href="([^"]*)',outbox[0].body).group(1)
            self.assertTrue(self.validateUri.startswith("https://localhost.local/v1/verify_email/"))
        with app.test_client() as c:
            user = User.getByEmail(email)
            creds = Credential.getByUser(user)
            assurances = Assurance.getByUser(user)
            self.assertTrue(assurances.has_key('emailverification') is False)
            resp = c.get(self.validateUri)
            self.assertEqual(user.email, email)
            newcreds = Credential.getByUser(user)
            self.assertEquals(len(creds) - 1 , len(newcreds))
            assurances = Assurance.getByUser(user)
            self.assertTrue(assurances['emailverification'] is not None)
            user.rm()

    @test
    def bad_email_uri_signals_error(self):
        with app.test_client() as c:
            resp = c.get("https://localhost.local/v1/verify_email/badkey")
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(self.getResponseText(resp),'{"errors": "unknown token"}')

    @test
    def users_with_assurer_assurance_can_get_email_and_digest_for_anyone(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            targetuser=self.create_user_with_credentials()
            Assurance.new(targetuser,'test',current_user)
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/users/{0}'.format(target.id))
            text = self.getResponseText(resp)
            data = json.loads(text)
            assurances = data['assurances']
            self.assertEquals(assurances['test'][0]['assurer'], current_user.email)

    @test
    def users_without_assurer_assurance_cannot_get_email_and_digest_for_anyone(self):
        with app.test_client() as c:
            self.login(c)
            targetuser=self.create_user_with_credentials()
            Assurance.new(targetuser,'test',current_user)
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/users/{0}'.format(target.id))
            self.assertEqual(403, resp.status_code)

    @test
    def users_with_assurer_assurance_can_get_user_by_email(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            self.setupRandom()
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertUserResponse(resp)

    @test
    def users_without_assurer_assurance_cannot_get_user_by_email(self):
        with app.test_client() as c:
            self.login(c)
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertEquals(resp.status_code,403)

    @test
    def users_without_login_cannot_get_user_by_email(self):
        with app.test_client() as c:
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertEquals(resp.status_code,302)
            self.assertEquals(resp.headers['Location'],"http://localhost.local/login")

    @test
    def assurance_form_needs_csrf(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                digest = "unimportant",
                assurance = "test",
                email = "unimportant",
                csrf_token = "")
            resp = c.post('http://localhost.local/v1/add_assurance', data = data)
            self.assertEquals(400, resp.status_code)
            self.assertEquals(self.getResponseText(resp),'{"errors": {"csrf_token": ["csrf validation error"]}}')

    @test
    def assurers_with_appropriate_credential_can_add_assurance_to_user(self):
        """
        the appropriate credential is an assurance in the form "assurer.<assurance_name>"
        where assurance_name is the assurance to be added
        """
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            Assurance.new(current_user, 'assurer.test', current_user)
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            target.hash="lkajsdlsajkhvdsknjdsflkjhfsaldkjslak"
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            self.assertTrue(Assurance.getByUser(target).has_key('test') is False)
            resp = c.post('http://localhost.local/v1/add_assurance', data = data)
            self.assertEquals(200, resp.status_code)
            self.assertEquals(Assurance.getByUser(target)['test'][0]['assurer'], current_user.email)

    @test
    def assurers_without_appropriate_credential_cannot_add_assurance_to_user(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            Assurance.new(current_user, 'assurer.testno', current_user)
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            target.hash="lkajsdlsajkhvdsknjdsflkjhfsaldkjslak"
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            self.assertTrue(Assurance.getByUser(target).has_key('test') is False)
            resp = c.post('http://localhost.local/v1/add_assurance', data = data)
            self.assertEquals(403, resp.status_code)
