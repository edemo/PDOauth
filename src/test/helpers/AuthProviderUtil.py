# pylint: disable=no-member
from pdoauth.models.Application import Application
from test.helpers.FakeInterFace import FakeForm

class AuthProviderUtil(object):

    authInterfaceInputMatrix = [
        ['response_type', None, 302, "Missing parameter response_type in URL query"],
        ['response_type', 'bad_type', 302, "unsupported_response_type"],
        ['client_id', None, 302, "Missing parameter client_id in URL query"],
        ['client_id', 'bad_client_id', 302, "Invalid request"],
        ['redirect_uri', None, 400, "Missing parameter redirect_uri in URL query"],
        ['redirect_uri', 'https://bad.redirect.com/uri', 302, "Invalid request"],
    ]

    tokenInterfaceInputMatrix = [
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
        code = data['code'][0]
        return code

    def callAuthInterface(self):
        code = self.getCodeFromAuthInterface(self.authParams)
        return code

    def assertCorrectKeysInTokenReply(self, data):
        keys = set(data.keys())
        for key in 'access_token', 'token_type', 'expires_in', 'refresh_token':
            keys.remove(key)
        self.assertEqual(len(keys), 0)

    def showUserByServer(self, tokens):
        headers = dict(Authorization='Bearer {0}'.format(tokens['access_token']))
        self.controller.interface.set_request_context(headers=headers)
        self.controller.authenticateUserOrBearer()
        resp = self.controller.doShowUser(userid='me')
        userinfo = self.fromJson(resp)
        return userinfo

    def prepareGetUserInfo(self):
        self.app = self.createApp()
        self.setDefaultParams()
        self.controller.loginInFramework(self.cred)

    def getUserInfo(self):
        tokens = self.obtainCodeAndCallTokenInterface()
        userinfo = self.showUserByServer(tokens)
        return userinfo
