# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.main import unauthorized, load_user
from urllib import urlencode
from test.TestUtil import UserTesting

class AuthTest(Fixture,UserTesting):
    @test
    def unauthorized_response_is_redirecting_to_login_page(self):
        with app.test_request_context('/'):
            resp = unauthorized()
            self.assertEquals(resp.status_code, 302)
            targetUri = "/static/login.html?{0}".format(urlencode(
                {"next": app.config.get("BASE_URL")+"/"
                }
            ))
            self.assertEquals(resp.headers['Location'], targetUri)

    @test
    def load_user_loads_the_user_by_id(self):
        user = self.createUserWithCredentials()
        loaded = load_user(user.userid)
        self.assertEquals(user,loaded)

    @test
    def load_user_returns_None_for_nonexisting_id(self):
        loaded = load_user("nonexisting")
        self.assertEquals(None,loaded)
