# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.main import unauthorized, load_user
from urllib import urlencode
from test.helpers.todeprecate.UserTesting import UserTesting

class AuthTest(Fixture, UserTesting):
    @test
    def unauthorized_response_is_redirecting_to_START_URL(self):
        "more specifically to START_URL?next={request.url}"
        testUrl = app.config.get("BASE_URL") + "/"
        with app.test_request_context("/", base_url=app.config.get("BASE_URL")):
            resp = unauthorized()
            self.assertEquals(resp.status_code, 302)
            targetUri = "{1}?{0}".format(
                urlencode(dict(next=testUrl)),
                app.config.get("START_URL")
            )
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
