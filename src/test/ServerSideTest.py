# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Application import Application
import config
from test.helpers.ServerSide import ServerSide
from test.helpers.todeprecate.UserTesting import UserTesting

class ServerSideTest(Fixture, UserTesting, ServerSide):

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
            resp = serverside.get(config.base_url + "/v1/users/me", headers=[('Authorization', '{0} {1}'.format(data['token_type'], data['access_token']))])
            self.assertEquals(resp.status_code, 200)
            data = self.fromJson(resp)
            self.assertTrue(data.has_key('userid'))

    @test
    def Unauthenticated_user_is_redirected_to_login_page_when_tries_to_do_oauth_with_us(self):
        redirectUri = 'https://client.example.com/oauth/redirect'
        self.setupRandom()
        appid = "app2-{0}".format(self.randString)
        self.appsecret = "secret2-{0}".format(self.randString)
        Application.new(appid, self.appsecret, redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect".format(appid)
        resp = app.test_client().get(uri)
        self.assertEquals(302,resp.status_code)
        self.assertTrue(resp.headers.has_key('Content-Length'))
        self.assertTrue(resp.headers['Location'].startswith(config.base_url + "/static/login.html"))

