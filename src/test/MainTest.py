
from twatson.unittest_annotations import Fixture, test

from pdoauth.app import app
from pdoauth.models.Application import Application
from pdoauth import main  # @UnusedImport

class MainTest(Fixture):


    def setUp(self):
        self.app = app.test_client()

    @test
    def NoRootUri(self):
        resp = self.app.get("/")
        self.assertEquals(resp.status_code, 404,)

    @test #will be a longer trip, because authentication should be implemented before this
    def get_authorization_code(self):
        redirectUri = 'https://client.example.com/oauth/redirect'
        Application.new('app','secret',redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id=app&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect"
        resp = self.app.get(uri)
        self.assertEquals(302,resp.status_code)
        self.assertTrue(resp.headers.has_key('Content-Length'))
        print "Location: {0}".format(resp.headers['Location'])
        self.assertTrue(resp.headers['Location'].startswith(redirectUri))