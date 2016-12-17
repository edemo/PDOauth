# -*- coding: UTF-8 -*-
from integrationtest.helpers.UserTesting import UserTesting
from pdoauth.app import app
from integrationtest.helpers.IntegrationTest import IntegrationTest
from integrationtest import config
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.WebInterface import WebInterface

class ServerSideTest(IntegrationTest, UserTesting, AuthProviderUtil):

    def setUp(self):
        IntegrationTest.setUp(self)
        self.app = self.createApp()
        self.setDefaultParams()

    
    def test_authorization_code_can_be_obtained_by_an_authenticated_user_using_correct_client_id_and_redirect_uri(self):
        self.getCode()

    def callMe(self, data):
        headers = {'Authorization':'{0} {1}'.format(
                data['token_type'],
                data['access_token'])}
        with app.test_client() as client:
            resp = client.get('/v1/users/me', headers=headers)
        return resp

    
    def test_you_can_get_user_info_with_authorization_code(self):
        resp = self.getCode()
        code = resp.headers['Location'].split('=')[1]
        resp = self.callTokenInterface(dict(), code)
        data = self.fromJson(resp)
        resp = self.callMe(data)
        self.assertEqual(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue('userid' in data)


    
    def test_token_interface_does_not_allow_bad_parameters(self):
        for paramupdates, status, message in self.tokenInterfaceInputMatrix:
            self.setUp()
            print("the parameters {0} lead to {1} {2}".format(paramupdates, status, message))
            resp = self.callTokenInterface(paramupdates, code='unused')
            responseData = self.fromJson(resp)
            self.assertEqual(responseData['errors'], message)
            self.assertEqual(resp.status_code, status)

    
    def test_for_access_token_you_need_a_refresh_token(self):
        with app.test_client() as client:
            self.app = self.createApp()
            appid = self.app.appid
            appsecret = self.app.secret
            tokenParams = dict(grant_type="refresh_token", client_id=appid, client_secret=appsecret)
            resp = client.post("/v1/oauth2/token", data=tokenParams)
        self.assertEqual(400, resp.status_code)

    
    def test_access_token_can_be_obtained_with_refresh_token(self):
        with app.test_client() as client:
            #self.app = self.createApp()
            appid = self.app.appid
            appsecret = self.app.secret
            resp = self.getCode()
            code = resp.headers['Location'].split('=')[1]
            paramupdates= dict()
            resp = self.callTokenInterface(paramupdates, code=code)
            responseData = self.fromJson(resp)
            self.assertTrue('refresh_token' in responseData)
            refresh_token=responseData['refresh_token']
            tokenParams = dict(grant_type="refresh_token", client_id=appid, client_secret=appsecret, refresh_token=refresh_token)
            resp = client.post("/v1/oauth2/token", data=tokenParams)
        responseData = self.fromJson(resp)
        self.assertTrue('access_token' in responseData)
        self.assertEqual(resp.status_code, 200)

    
    def test_access_token_can_be_obtained_with_refresh_token_even_when_the_app_and_user_have_a_token_in_file(self):
        with app.test_client() as client:
            #self.app = self.createApp()
            appid = self.app.appid
            appsecret = self.app.secret
            self.getCode()
            resp = self.getCode()
            code = resp.headers['Location'].split('=')[1]
            paramupdates= dict()
            resp = self.callTokenInterface(paramupdates, code=code)
            responseData = self.fromJson(resp)
            self.assertTrue('refresh_token' in responseData)
            refresh_token=responseData['refresh_token']
            tokenParams = dict(grant_type="refresh_token", client_id=appid, client_secret=appsecret, refresh_token=refresh_token)
            resp = client.post("/v1/oauth2/token", data=tokenParams)
        responseData = self.fromJson(resp)
        self.assertTrue('access_token' in responseData)
        self.assertEqual(resp.status_code, 200)

    def getCode(self):
        with app.test_client() as client:
            self.login(client)
            baseUri = config.BASE_URL + '/v1/oauth2/auth'
            uri = WebInterface.parametrizeUri(baseUri, self.authParams)
            resp = client.get(uri)
            return resp

    
    def test_auth_interface_does_not_allow_bad_parameters(self):
        for param, value, status, message in self.authInterfaceInputMatrix:
            self.setUp()
            print("{1} as {0} leads to {2} {3}".format(param, value, status, message))
            if value is None:
                self.authParams.pop(param)
            else:
                self.authParams[param] = value
            resp = self.getCode()
            self.assertEqual(status, resp.status_code)
            if status == 302:
                location = resp.headers['Location']
                self.assertTrue(message.replace(' ', '%20') in location)
            else:
                self.assertEqual(self.getResponseText(resp), '{{"errors": "{0}"}}'.format(message))
