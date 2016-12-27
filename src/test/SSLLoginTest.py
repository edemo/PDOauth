# pylint: disable=line-too-long
from pdoauth.models.Credential import Credential
from test.helpers.PDUnitTest import PDUnitTest

from test.config import Config
from test.helpers.FakeInterFace import FakeMail
from test.helpers.CryptoTestUtil import CryptoTestUtil, TEST_USER_IDENTIFIER
from test.helpers.UserUtil import UserUtil
from pdoauth.Messages import errorInCert
import uritools

CREDENTIAL_REPRESENTATION = '{{"credentialType": "certificate", "identifier": "{0}"}}'.format(TEST_USER_IDENTIFIER)

class SslLoginTest(PDUnitTest, CryptoTestUtil, UserUtil):

    def tearDown(self):
        PDUnitTest.tearDown(self)
        self.removeCertUser()

    
    def test_there_is_a_SSL_LOGIN_BASE_URL_config_option_containing_the_base_url_of_the_site_with_the_optional_no_ca_config(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL is not None)

    
    def test_there_is_a_BASE_URL_config_option_containing_the_plain_ssl_base_url(self):
        "where no certificate is asked"
        self.assertTrue(Config.BASE_URL is not None)

    
    def test_there_is_a_SSL_LOGOUT_URL_config_option_pointing_to_a_location_which_is_set_up_with_SSLVerifyClient_require_and_SSLVerifyDepth_0_within_SSL_LOGIN_BASE_URL(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL in Config.SSL_LOGOUT_URL)

    
    def test_there_is_a_START_URL_config_option_which_contains_the_starting_point_useable_for_unregistered_and_or_not_logged_in_user(self):
        self.assertTrue(Config.BASE_URL in Config.START_URL)

    
    def test_you_can_login_using_a_registered_ssl_cert(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(CREDENTIAL_REPRESENTATION in
            self.getResponseText(resp))

    
    def test_ssl_login_sets_csrf_cookie(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        self.assertTrue('csrf' in cookieParts)

    
    def test_login_cookie_have_path_set_to_root(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        self.assertEqual(cookieParts['Path'], '/')

    
    def test_login_cookie_have_domain_set_to_COOKIE_DOMAIN(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        cookieDomain = self.controller.app.config.get('COOKIE_DOMAIN')
        self.assertEqual(cookieParts['Domain'], cookieDomain)

    def test_with_cert_login_you_get_actually_logged_in(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEqual(resp.status_code, 200)
        body = self.getResponseText(resp)
        self.assertIn(CREDENTIAL_REPRESENTATION,
            body)
        resp = self.showUserByCurrentUser('me')
        self.assertEqual(200, resp.status_code)

    
    def test_you_cannot_login_using_an_unregistered_ssl_cert_without_email(self):
        certAttr = self.getCertAttributes()
        self.assertReportedError(
            self.sslLoginWithCert, [certAttr.cert], 403, ["You have to register first"])

    
    def test_you_cannot_login_without_a_cert(self):
        self.assertReportedError(
            self.controller.doSslLogin, [], 400, errorInCert)

    
    def test_empty_certstring_gives_error(self):
        self.assertReportedError(
            self.sslLoginWithCert, [''], 400, errorInCert)

    
    def test_junk_certstring_gives_error(self):
        self.assertReportedError(
            self.sslLoginWithCert, ['junk'], 400, errorInCert)

    
    def test_ssl_login_is_cors_enabled(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Access-Control-Allow-Origin'], "*")

    
    def test_you_can_register_and_login_using_an_unregistered_ssl_cert_with_email(self):
        certAttr = self.getCertAttributes()
        params=dict(email="certuser@example.com")
        parts = uritools.urisplit(Config.BASE_URL)
        url = uritools.uricompose(parts.scheme, parts.host, parts.path, params)
        self.controller.interface.set_request_context(url)
        self.controller.mail = FakeMail()
        resp = self.sslLoginWithCert(certAttr.cert)
        cred = Credential.get("certificate", certAttr.identifier)
        self.deleteUser(cred.user)
        self.assertEqual(resp.status_code, 200)
        responseText = self.getResponseText(resp)
        self.assertTrue(CREDENTIAL_REPRESENTATION in
            responseText)
        self.assertTrue('{"credentialType": "emailcheck", "identifier":' in
            responseText)
