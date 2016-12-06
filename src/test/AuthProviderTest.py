# -*- coding: UTF-8 -*-
from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.UserUtil import UserUtil
from pdoauth.AuthProvider import AuthProvider
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.models.Application import Application
from test import config
from test.helpers.FakeInterFace import FakeInterface, FakeApp
from pdoauth.ReportedError import ReportedError

class AuthProviderTest(PDUnitTest, UserUtil, AuthProviderUtil):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.app = self.createApp()
        self.createLoggedInUser()
        self.authProvider = AuthProvider(self.controller.interface)
        self.authProvider.app = FakeApp()
        self.setDefaultParams()

    
    def test_code_can_be_obtained_in_auth_interface(self):
        self.callAuthInterface()

    
    def test_tokens_can_be_obtained_in_token_interface_with_code(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.assertTrue('access_token' in data)

    
    def test_token_interface_response_contains_access_token__token_type__expires_in_and_refresh_token(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.assertCorrectKeysInTokenReply(data)

    
    def test_tokens_can_be_obtained_in_token_interface_with_refresh_token(self):
        data = self.obtainCodeAndCallTokenInterface()
        self.setDefaultParams()
        self.tokenParams['grant_type'] = 'refresh_token'
        data = self.callJustTokenInterface(False, data['refresh_token'])
        self.assertCorrectKeysInTokenReply(data)

    
    def test_all_parameters_for_auth_interface_should_be_present_and_correct(self):
        for param, value, status, message in self.authInterfaceInputMatrix:
            self.setDefaultParams()
            print("{1} as {0} leads to {2} {3}".format(param, value, status, message))
            if value is None:
                self.authParams.pop(param)
            else:
                self.authParams[param] = value
            self.assertReportedError(self.getCodeFromAuthInterface,[self.authParams],
                status, message)

    
    def test_auth_interface_does_not_work_without_login(self):
        self.controller.logOut()
        self.assertReportedError(self.callAuthInterface, (), 302, 'access_denied')

    
    def test_bad_parameters_in_token_interface_lead_to_errors(self):
        for paramupdates, status, message in self.tokenInterfaceInputMatrix:
            self.setUp()
            print("the parameters {0} lead to {1} {2}".format(paramupdates, status, message))
            self.tokenParams.update(paramupdates)
            self.assertReportedError(self.obtainCodeAndCallTokenInterface,[],status,message)

    
    def test_refresh_token_cannot_be_obtained_with_another_clients_identity(self):
        self.tokenParams['grant_type'] = 'refresh_token'
        app = self.createApp()
        self.tokenParams['client_id'] = app.appid
        self.tokenParams['client_secret'] = app.secret
        self.assertReportedError(self.obtainCodeAndCallTokenInterface,[],400,'invalid_grant')

    
    def test_no_scope_equals_empty_scope(self):
        self.tokenParams['scope'] = None
        data = self.obtainCodeAndCallTokenInterface()
        self.assertCorrectKeysInTokenReply(data)

    
    def test_unauthenticated_user_is_redirected_to_login_page_when_tries_to_do_oauth_with_us_2(self):
        controller=AuthProvider(FakeInterface())
        controller.app = FakeApp()
        redirectUri = 'https://client.example.com/oauth/redirect'
        self.setupRandom()
        appid = "app2-{0}".format(self.randString)
        self.appsecret = "secret2-{0}".format(self.randString)
        app = Application.new(appid, self.appsecret, redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect".format(app.appid)
        controller.interface.set_request_context(url=uri)
        with self.assertRaises(ReportedError) as e:
            controller.auth_interface()
        self.assertEqual(302,e.exception.status)
        self.assertTrue(e.exception.uri.startswith(config.Config.BASE_URL + "/static/login.html"))
