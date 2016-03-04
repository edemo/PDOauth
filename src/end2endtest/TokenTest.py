from twatson.unittest_annotations import Fixture, test
import json
from helpers.BrowsingUtil import BrowsingUtil, TE
import urllib2
import urllib
from pdoauth.models.User import User
from pdoauth.models.AppMap import AppMap

class TokenTest(Fixture,BrowsingUtil):

    def getOauthToken(self, app):
        code = TE.driver.current_url.split('=')[1]
        fields = dict(code=code, grant_type='authorization_code', 
            client_id=app.appid, 
            client_secret=app.secret, 
            redirect_uri=app.redirect_uri)
        url = TE.backendUrl + "/v1/oauth2/token"
        req = urllib2.urlopen(url, urllib.urlencode(fields))
        resp = req.read()
        answer = json.loads(resp)
        return answer

    def obtainAccessToken(self):
        app = TE.app
        self.callOauthUri()
        self.registerUser()
        self.waitFortestAppRedirectUri()
        self.assertTrue(TE.driver.current_url.startswith(app.redirect_uri))
        answer = self.getOauthToken(app)
        return answer

    @test
    def the_server_can_get_your_access_tokens_using_your_authorization_code(self):
        answer = self.obtainAccessToken()
        self.assertEqual(answer['token_type'], "Bearer")
        self.assertEqual(answer['expires_in'], 3600)
        self.accessToken = answer['access_token']
        self.refreshToken = answer['refresh_token']

    @test
    def the_server_can_get_your_user_info_with_your_access_token(self):
        accessToken = self.obtainAccessToken()['access_token']
        req = urllib2.Request(TE.backendUrl + "/v1/users/me")
        req.add_header('Authorization', 'Bearer {0}'.format(accessToken))
        resp = urllib2.urlopen(req).read()
        answer = json.loads(resp)
        user = User.getByEmail(self.userCreationEmail)
        appMapEntry = AppMap.get(TE.app, user)
        self.assertEqual(answer['email'], appMapEntry.getEmail())
        self.assertEqual(answer['assurances'], [])

    def tearDown(self):
        BrowsingUtil.tearDown(self)