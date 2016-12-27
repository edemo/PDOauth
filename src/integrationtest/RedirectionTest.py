# pylint: disable=maybe-no-member
from integrationtest.helpers.IntegrationTest import IntegrationTest
from pdoauth.models.Application import Application
from pdoauth.app import app
from integrationtest import config
from test.helpers.RandomUtil import RandomUtil

class RedirectionTest(IntegrationTest, RandomUtil):
    
    def test_unauthenticated_user_is_redirected_to_login_page_when_tries_to_do_oauth_with_us(self):
        redirectUri = 'https://client.example.com/oauth/redirect'
        self.setupRandom()
        appid = "app2-{0}".format(self.randString)
        self.appsecret = "secret2-{0}".format(self.randString)
        Application.new(appid, self.appsecret, redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect".format(appid)
        resp = app.test_client().get(uri)
        self.assertEqual(302,resp.status_code)
        self.assertTrue('Content-Length' in resp.headers)
        locationHeader = resp.headers['Location']
        self.assertTrue(locationHeader.startswith(config.Config.LOGIN_URL))
