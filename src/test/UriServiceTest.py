
from pdoauth.app import app
from pdoauth import main  # @UnusedImport
from test.helpers.ResponseInfo import ResponseInfo
from test.helpers.PDUnitTest import PDUnitTest

class UriServiceTest(PDUnitTest, ResponseInfo):

    def _checkUri(self, checkedUri):
        resp = self.controller.doUris()
        self.assertEqual(resp.status_code, 200)
        uris = self.fromJson(resp)
        self.assertTrue(uris[checkedUri] is not None)
        self.assertEqual(uris[checkedUri], app.config.get(checkedUri))

    
    def test_the_uri_service_gives_back_the_BASE_URL(self):
        self._checkUri('BASE_URL')

    
    def test_the_uri_service_gives_back_the_SSL_LOGIN_BASE_URL(self):
        self._checkUri('SSL_LOGIN_BASE_URL')

    
    def test_the_uri_service_gives_back_the_PASSWORD_RESET_FORM_URL(self):
        self._checkUri('PASSWORD_RESET_FORM_URL')

    
    def test_the_uri_service_gives_back_the_START_URL(self):
        self._checkUri('START_URL')

    
    def test_the_uri_service_gives_back_the_SSL_LOGOUT_URL(self):
        self._checkUri('SSL_LOGOUT_URL')

    
    def test_the_uri_service_gives_back_the_ANCHOR_URL(self):
        self._checkUri('ANCHOR_URL')

    
    def test_the_uri_service_gives_back_the_FACEBOOK_APP_ID(self):
        self._checkUri('FACEBOOK_APP_ID')

    
    def test_the_uri_service_gives_back_the_BACKEND_PATH(self):
        self._checkUri('BACKEND_PATH')

    
    def test_the_uri_service_gives_back_the_LOGIN_URL(self):
        self._checkUri('LOGIN_URL')
