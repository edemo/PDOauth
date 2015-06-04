
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth import main  # @UnusedImport
from test.helpers.ResponseInfo import ResponseInfo

class UriServiceTest(Fixture, ResponseInfo):

    def _checkUri(self, c, checkedUri):
        resp = c.get("/uris")
        self.assertEquals(resp.status_code, 200)
        uris = self.fromJson(resp)
        self.assertTrue(uris[checkedUri] is not None)
        self.assertEqual(uris[checkedUri], app.config.get(checkedUri))

    @test
    def the_uri_service_gives_back_the_BASE_URL(self):
        with app.test_client() as c:
            self._checkUri(c, 'BASE_URL')

    @test
    def the_uri_service_gives_back_the_SSL_LOGIN_BASE_URL(self):
        with app.test_client() as c:
            self._checkUri(c, 'SSL_LOGIN_BASE_URL')

    @test
    def the_uri_service_gives_back_the_PASSWORD_RESET_FORM_URL(self):
        with app.test_client() as c:
            self._checkUri(c, 'PASSWORD_RESET_FORM_URL')

    @test
    def the_uri_service_gives_back_the_START_URL(self):
        with app.test_client() as c:
            self._checkUri(c, 'START_URL')

    @test
    def the_uri_service_gives_back_the_SSL_LOGOUT_URL(self):
        with app.test_client() as c:
            self._checkUri(c, 'SSL_LOGOUT_URL')
