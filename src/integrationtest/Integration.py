from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.models.Application import Application
from pdoauth.app import app
import config
from test.helpers.RandomUtil import RandomUtil

class Integration(IntegrationTest, RandomUtil):
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

