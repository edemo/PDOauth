# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth import auth
from pdoauth.app import app
from pdoauth.models.User import User
from bs4 import BeautifulSoup
from test.TestUtil import CSRFMixin
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



class LoginTest(Fixture,CSRFMixin):
    def setUp(self):
        Credential.query.delete()  # @UndefinedVariable
        User.query.delete()  # @UndefinedVariable
    @test
    def password_login_needs_csrf(self):
        with app.test_request_context('/', data=dict(username="user",password="a password"), method="POST"):
            resp = auth.do_login()
            soup = BeautifulSoup(resp)
            div = unicode(soup.find(id="flashed").li)
            self.assertTrue(u"<li>Error in the Csrf Token field - CSRF token missing </li>" in div)

    @test
    def login_with_get_does_not_err(self):
        with app.test_request_context('/', method="GET"):
            resp = auth.do_login()
            soup = BeautifulSoup(resp)
            div = soup.find(id="flashed")
            self.assertEquals(div,None)

    @test
    def password_login_needs_username(self):
        with app.test_client() as c:
            csrf = self.getCSRF(c)
            data = dict(csrf_token=csrf, password="password")
            c.post('/vi/login', data=data)
            resp = auth.do_login()
            soup = BeautifulSoup(resp)
            div = unicode(soup.find(id="flashed").li)
            self.assertTrue(u"Error in the username field"  in div)
            self.assertEquals(
                u'<div id="usernameerrors">\n<span style="color: red;">[Field must be between 4 and 25 characters long.]</span>\n</div>',
                unicode(soup.find(id="usernameerrors")))

    @test
    def password_login_needs_password(self):
        with app.test_client() as c:
            csrf = self.getCSRF(c)
            data = dict(csrf_token=csrf, username="userid")
            c.post('/vi/login', data=data)
            resp = auth.do_login()
            soup = BeautifulSoup(resp)
            div = unicode(soup.find(id="flashed").li)
            self.assertTrue(u"Error in the password field" in div)
            self.assertEquals(
                u'<div id="passworderrors">\n<span style="color: red;">[Field must be at least 8 characters long.]</span>\n</div>',
                unicode(soup.find(id="passworderrors")))

    @test
    def password_login_needs_correct_username_and_password(self):
        with app.test_client() as c:
            csrf = self.getCSRF(c)
            data = dict(csrf_token=csrf, username="userid", password="password")
            c.post('/vi/login', data=data)
            resp = auth.do_login()
            soup = BeautifulSoup(resp)
            div = unicode(soup.find(id="flashed").li)
            self.assertTrue(u"Bad username or password" in div)

    @test
    def password_login_works_with_correct_username_and_password(self):
        user = CredentialManager.create_user_with_creds("password", "userid", "passwordka", "kukac@example.com")
        user.activate()
        with app.test_client() as c:
            csrf = self.getCSRF(c)
            data = dict(csrf_token=csrf, username="userid", password="passwordka")
            c.post('/vi/login', data=data)
            resp = auth.do_login()
            self.assertEquals(resp.status_code,302)
            self.assertEquals(resp.headers['Location'], '/')

#FIXME: test auth.email_verification(user)
#FIXME: test auth.do_registration()
#FIXME:test auth.isAllowedToGetUser()
#FIXME: test auth.flash_errors(form)