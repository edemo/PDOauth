# -*- coding: UTF-8 -*-
from integrationtest.helpers.UserTesting import UserTesting
from pdoauth.app import app
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest import config
import urllib
from test.helpers.AuthProviderUtil import AuthProviderUtil

class ServerSideTest(IntegrationTest, UserTesting, AuthProviderUtil):

    def setUp(self):
        IntegrationTest.setUp(self)
        self.app = self.createApp()
        self.setDefaultParams()

    @test
    def authorization_code_can_be_obtained_by_an_authenticated_user_using_correct_client_id_and_redirect_uri(self):
        self.getCode()

    def callMe(self, data):
        headers = {'Authorization':'{0} {1}'.format(
                data['token_type'],
                data['access_token'])}
        with app.test_client() as client:
            resp = client.get('/v1/users/me', headers=headers)
        return resp

    @test
    def you_can_get_user_info_with_authorization_code(self):
        resp = self.getCode()
        code = resp.headers['Location'].split('=')[1]
        resp = self.callTokenInterface(dict(), code)
        data = self.fromJson(resp)
        resp = self.callMe(data)
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('userid'))


    @test
    def token_interface_does_not_allow_bad_parameters(self):
        for paramupdates, status, message in self.tokenInterfaceInputMatrix:
            self.setUp()
            print "the parameters {0} lead to {1} {2}".format(paramupdates, status, message)
            resp = self.callTokenInterface(paramupdates, code='unused')
            responseData = self.fromJson(resp)
            self.assertEqual(responseData['errors'], message)
            self.assertEqual(resp.status_code, status)

    @test
    def for_access_token_you_need_a_refresh_token(self):
        with app.test_client() as client:
            self.app = self.createApp()
            appid = self.app.appid
            appsecret = self.app.secret
            tokenParams = dict(grant_type="refresh_token", client_id=appid, client_secret=appsecret)
            resp = client.post("/v1/oauth2/token", data=tokenParams)
        self.assertEqual(400, resp.status_code)

    @test
    def access_token_can_be_obtained_with_refresh_token(self):
        with app.test_client() as client:
            #self.app = self.createApp()
            appid = self.app.appid
            appsecret = self.app.secret
            resp = self.getCode()
            code = resp.headers['Location'].split('=')[1]
            paramupdates= dict()
            resp = self.callTokenInterface(paramupdates, code=code)
            responseData = self.fromJson(resp)
            self.assertTrue(responseData.has_key('refresh_token'))
            refresh_token=responseData['refresh_token']
            tokenParams = dict(grant_type="refresh_token", client_id=appid, client_secret=appsecret, refresh_token=refresh_token)
            resp = client.post("/v1/oauth2/token", data=tokenParams)
        responseData = self.fromJson(resp)
        self.assertTrue(responseData.has_key('access_token'))
        self.assertEqual(resp.status_code, 200)

    def getCode(self):
        with app.test_client() as client:
            self.login(client)
            baseUri = config.BASE_URL + '/v1/oauth2/auth'
            resp = client.get(baseUri, query_string=urllib.urlencode(self.authParams))
            return resp

    @test
    def auth_interface_does_not_allow_bad_parameters(self):
        for param, value, status, message in self.authInterfaceInputMatrix:
            self.setUp()
            print "{1} as {0} leads to {2} {3}".format(param, value, status, message)
            if value is None:
                self.authParams.pop(param)
            else:
                self.authParams[param] = value
            if self.authParams.has_key('redirect_uri'):
                redirectUri = self.authParams['redirect_uri']
            resp = self.getCode()
            self.assertEqual(status, resp.status_code)
            if status == 302:
                location = resp.headers['Location']
                self.assertEqual(location, redirectUri + '?errors='+message.replace(' ', '%20'))
            else:
                self.assertEqual(self.getResponseText(resp), '{{"errors": "{0}"}}'.format(message))
