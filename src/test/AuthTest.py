# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth import auth
from pdoauth.app import app
from pdoauth.models.User import User
from test.TestUtil import ResponseInfo, UserTesting
from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Credential import Credential

class AuthTest(Fixture):
    @test
    def unauthorized_response_is_redirecting_to_login_page(self):
        with app.test_request_context('/'):
            resp = auth.unauthorized()
            self.assertEquals(resp.status_code, 302)
            self.assertEquals(resp.headers['Location'], "/login")

    @test
    def load_user_loads_the_user_by_id(self):
        user = User.new(email="email@example.org")
        loaded = auth.load_user(user.id)
        self.assertEquals(user,loaded)

    @test
    def load_user_returns_None_for_nonexisting_id(self):
        loaded = auth.load_user("nonexisting")
        self.assertEquals(None,loaded)



class LoginTest(Fixture, UserTesting):
    def setUp(self):
        Credential.query.delete()  # @UndefinedVariable
        User.query.delete()  # @UndefinedVariable

    @test
    def login_does_not_accept_get(self):
        with app.test_client() as c:
            resp = c.get("/v1/login")
            self.assertEquals(resp.status_code, 404)

    @test
    def password_login_needs_username(self):
        with app.test_client() as c:
            data = dict(password="password")
            resp = c.post('http://localhost.local/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": {"username": ["'))

    @test
    def password_login_needs_password(self):
        with app.test_client() as c:
            data = dict(username="userid")
            resp = c.post('http://localhost.local/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertTrue(text.startswith('{"errors": {"password": ["'))

    @test
    def password_login_needs_correct_username_and_password(self):
        with app.test_client() as c:
            data = dict(username="userid", password="password")
            resp = c.post('http://localhost.local/login', data=data)
            self.assertEquals(resp.status_code, 403)
            text = self.getResponseText(resp)
            self.assertEquals(text,'{"errors": "Bad username or password"}')

    @test
    def password_login_works_with_correct_username_and_password(self):
        user = CredentialManager.create_user_with_creds("password", "userid", "passwordka", "kukac@example.com")
        user.activate()
        with app.test_client() as c:
            data = dict(username="userid", password="passwordka")
            resp = c.post('http://localhost.local/login', data=data)
            self.assertUserResponse(resp)

#FIXME: test auth.email_verification(user)
#FIXME: test auth.do_registration()
#FIXME:test auth.isAllowedToGetUser()
#FIXME: test auth.flash_errors(form)