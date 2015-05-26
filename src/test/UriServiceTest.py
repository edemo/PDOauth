from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app

class UriServiceTest(Fixture, UserTesting):

    @test
    def the_uri_service_gives_back_the_base_url(self):
        with app.test_client() as c:
            resp = c.get("/uris")
            self.assertEquals(resp.status_code, 200)
            uris = self.fromJson(resp)
            self.assertEqual(uris['BASE_URL'], app.config.get('BASE_URL'))

    @test
    def the_uri_service_gives_back_the_ssl_login_url(self):
        with app.test_client() as c:
            resp = c.get("/uris")
            self.assertEquals(resp.status_code, 200)
            uris = self.fromJson(resp)
            self.assertEqual(uris['SSL_LOGIN_URL'], app.config.get('SSL_LOGIN_URL'))
