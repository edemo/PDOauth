# -*- coding: UTF-8 -*-
from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.models.Application import Application
from test.helpers.UserUtil import UserUtil
from pdoauth.AuthProvider import AuthProvider
from test.helpers.FakeInterFace import FakeForm

class AuthProviderTest(PDUnitTest, UserUtil):


    def setDefaultParams(self):
        self.tokenParams = {
            "grant_type":'authorization_code',
            "client_id":self.app.appid,
            "client_secret":self.app.secret,
            "redirect_uri":self.app.redirect_uri,
            "scope":'',
            "refresh_token":None,
            'code':None}
        self.authParams = {
            "response_type":'code',
            "client_id":self.app.appid,
            "redirect_uri":self.app.redirect_uri}

    def setUp(self):
        PDUnitTest.setUp(self)
        self.app = self.createApp()
        self.createLoggedInUser()
        self.authProvider = AuthProvider(self.controller.interface)
        self.setDefaultParams()

    def callJustTokenInterface(self, code, data=None):
        self.controller.logOut()
        self.data = self.tokenParams
        self.addDataBasedOnOptionValue('code', self.tokenParams['code'], code)
        self.addDataBasedOnOptionValue('refresh_token', self.tokenParams['refresh_token'], data)
        form = FakeForm(self.data)
        resp = self.authProvider.token_interface(form)
        data = self.fromJson(resp)
        return data

    def obtainCodeAndCallTokenInterface(self):
        code = self.callAuthInterface()
        data = self.callJustTokenInterface(code)
        return data

    def createApp(self):
        appName = self.mkRandomString(5)
        appSecret = self.mkRandomString(15)
        redirect_uri = "https://{0}.example.com/redirect_uri".format(self.mkRandomString(8))
        app = Application.new(appName, appSecret, redirect_uri)
        return app

    def getCodeFromAuthInterface(self, params):
        baseUri = "https://localhost.local/v1/oauth2/auth"
        uri = self.controller.build_url(baseUri, params)
        self.controller.interface.set_request_context(uri, newUri=True)
        resp = self.authProvider.auth_interface()
        data = self.controller.getParamsOfUri(resp.headers['Location'])
        code = data['code']
        return code

    def callAuthInterface(self):
        code = self.getCodeFromAuthInterface(self.authParams)
        return code

    @test
    def code_can_be_obtained_in_auth_interface(self):
        self.callAuthInterface()

    @test
    def tokens_can_be_obtained_in_token_interface_with_code(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.assertTrue(data.has_key('access_token'))

    @test
    def token_interface_response_contains_access_token__token_type__expires_in_and_refresh_token(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.assertCorrectKeysInTokenReply(data)

    @test
    def tokens_can_be_obtained_in_token_interface_with_refresh_token(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.setDefaultParams()
        self.tokenParams['grant_type'] = 'refresh_token'
        data = self.callJustTokenInterface(False, data['refresh_token'])
        self.assertCorrectKeysInTokenReply(data)

    @test
    def all_parameters_for_auth_interface_should_be_present_and_correct(self):
        matrix = [
            ['response_type', None, 302, "Missing parameter response_type in URL query"],
            ['response_type', 'bad_type', 302, "unsupported_response_type"],
            ['client_id', None, 302, "Missing parameter client_id in URL query"],
            ['client_id', 'bad_client_id', 302, "Invalid request"],
            ['redirect_uri', None, 400, "Missing parameter redirect_uri in URL query"],
            ['redirect_uri', 'https://bad.redirect.com/uri', 302, "Invalid request"],
        ]

        for param, value, status, message in matrix:
            self.setDefaultParams()
            print "{1} as {0} leads to {2} {3}".format(param, value, status, message)
            if value is None:
                self.authParams.pop(param)
            else:
                self.authParams[param] = value
            self.assertReportedError(self.getCodeFromAuthInterface,[self.authParams],
                status, message)

    @test
    def auth_interface_does_not_work_without_login(self):
        self.controller.logOut()
        self.assertReportedError(self.callAuthInterface, (), 302, 'access_denied')

    def assertCorrectKeysInTokenReply(self, data):
        keys = data.keys()
        for key in 'access_token', 'token_type', 'expires_in', 'refresh_token':
            keys.remove(key)
        self.assertEqual(len(keys), 0)

    @test
    def bad_parameters_in_token_interface_lead_to_errors(self):
        matrix = [
            [dict(client_id='bad'), 400, 'invalid_grant'],
            [dict(client_id=None), 400, 'Missing required OAuth 2.0 POST param: client_id'],
            [dict(code='bad code'), 400, 'invalid_grant'],
            [dict(code=False), 400, 'invalid_grant'],
            [dict(scope='bad scope'), 400, 'invalid_scope'],
            [dict(grant_type=None), 400, 'Missing required OAuth 2.0 POST param: grant_type'],
            [dict(grant_type='badGrantType'), 400, 'unsupported_grant_type'],
            [dict(client_secret='badsecret'), 400, 'invalid_client'],
            [dict(client_secret=None), 400, 'Missing required OAuth 2.0 POST param: client_secret'],
            [dict(redirect_uri='https://bad.redirect/uri'), 400, 'invalid_grant'],
            [dict(redirect_uri=None), 400, 'Missing required OAuth 2.0 POST param: redirect_uri'],
            [dict(grant_type='refresh_token', client_secret='bad secret'), 400, 'invalid_client'],
            [dict(grant_type='refresh_token', scope='bad scope'), 400, 'invalid_scope'],
            [dict(grant_type='refresh_token', client_id=None), 400, 'Missing required OAuth 2.0 POST param: client_id'],
            [dict(grant_type='refresh_token', client_id='bad client id'), 400, 'unauthorized_client'],
            [dict(grant_type='refresh_token', client_secret=None), 400, 'Missing required OAuth 2.0 POST param: client_secret'],
        ]
        for paramupdates, status, message in matrix:
            self.setUp()
            print "the parameters {0} leads to {1} {2}".format(paramupdates, status, message)
            self.tokenParams.update(paramupdates)
            self.assertReportedError(self.obtainCodeAndCallTokenInterface,[],status,message)

    @test
    def refresh_token_cannot_be_obtained_with_another_clients_identity(self):
        self.tokenParams['grant_type'] = 'refresh_token'
        app = self.createApp()
        self.tokenParams['client_id'] = app.appid
        self.tokenParams['client_secret'] = app.secret
        self.assertReportedError(self.obtainCodeAndCallTokenInterface,[],400,'invalid_grant')

    @test
    def no_scope_equals_empty_scope(self):
        self.tokenParams['scope'] = None
        data = self.obtainCodeAndCallTokenInterface()
        self.assertCorrectKeysInTokenReply(data)

