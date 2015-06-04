# -*- coding: UTF-8 -*-
from pdoauth.models.Application import Application
import config
from test.helpers.ServerSide import ServerSide
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from pdoauth.AuthProvider import AuthProvider

class ServerSideTest(PDUnitTest, ServerSide, UserUtil):


    def createApplication(self):
        redirect_uri = 'https://test.app/redirecturi'
        appid = "app-{0}".format(self.randString)
        self.appsecret = "secret-{0}".format(self.randString)
        application = Application.new(appid, self.appsecret, redirect_uri)
        return application, redirect_uri

    def buildAuthUrl(self, redirect_uri):
        uri = config.base_url + '/v1/oauth2/auth'
        query_string = 'response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, redirect_uri)
        self.controller._testdata.request_url = uri + "?" + query_string

    def loginAndGetCode(self):
        self.current_user = self.createLoggedInUser()
        application, redirect_uri = self.createApplication()
        self.appid = application.appid
        self.buildAuthUrl(redirect_uri)
        resp = AuthProvider.auth_interface()
        self.assertEqual(302, resp.status_code)
        location = resp.headers['Location']
        self.assertTrue(location.startswith('https://test.app/redirecturi?code='))
        code = location.split('=')[1]
        return code

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
        self.controller._testdata.current_url = config.base_url + "/v1/users/me"
        self.controller._testdata.headers = {
            'Authorization': '{0} {1}'.format(
                    data['token_type'],
                    data['access_token']
                )
        }
        resp = self.controller._do_show_user('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('userid'))
