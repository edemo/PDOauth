from helpers.BrowsingUtil import BrowsingUtil, TE
from pdoauth.models.User import User
from pdoauth.models.AppMap import AppMap
from pdoauth.WebInterface import WebInterface
from unittest.case import TestCase
import requests

class TokenTest(TestCase,BrowsingUtil):

    def getOauthToken(self, app):
        code = TE.driver.current_url.split('=')[1]
        fields = dict(code=code, grant_type='authorization_code', 
            client_id=app.appid, 
            client_secret=app.secret, 
            redirect_uri=app.redirect_uri)
        url = WebInterface.parametrizeUri(TE.backendUrl + "/v1/oauth2/token", fields)
        resp = requests.post(url, fields, verify=False)
        answer = resp.json()
        return answer

    def obtainAccessToken(self):
        app = TE.app
        self.callOauthUri()
        self.registerUser(buttonId="section_changer_register")
        self.waitFortestAppRedirectUri()
        self.assertTrue(TE.driver.current_url.startswith(app.redirect_uri))
        answer = self.getOauthToken(app)
        return answer

    
    def test_the_server_can_get_your_access_tokens_using_your_authorization_code(self):
        answer = self.obtainAccessToken()
        self.assertEqual(answer['token_type'], "Bearer")
        self.assertEqual(answer['expires_in'], 3600)
        self.accessToken = answer['access_token']
        self.refreshToken = answer['refresh_token']

    
    def test_the_server_can_get_your_user_info_with_your_access_token(self):
        accessToken = self.obtainAccessToken()['access_token']
        url = TE.backendUrl + "/v1/users/me"
        headers = {'Authorization': 'Bearer {0}'.format(accessToken)}
        resp = requests.get(url, headers=headers, verify=False)
        answer = resp.json()
        user = User.getByEmail(self.userCreationEmail)
        appMapEntry = AppMap.get(TE.app, user)
        self.assertEqual(answer['email'], appMapEntry.getEmail())
        self.assertEqual(answer['assurances'], [])

    def tearDown(self):
        BrowsingUtil.tearDown(self)
