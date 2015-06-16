# pylint: disable=line-too-long
from pdoauth.models.Credential import Credential
from urllib import urlencode
from test.helpers.PDUnitTest import PDUnitTest, test

from test.config import Config
from test.helpers.FakeInterFace import FakeMail
from test.helpers.CryptoTestUtil import CryptoTestUtil, TEST_USER_IDENTIFIER
from test.helpers.UserUtil import UserUtil

CREDENTIAL_REPRESENTATION = '{{"credentialType": "certificate", "identifier": "{0}"}}'.format(TEST_USER_IDENTIFIER)

class SslLoginTest(PDUnitTest, CryptoTestUtil, UserUtil):

    def tearDown(self):
        PDUnitTest.tearDown(self)
        self.removeCertUser()

    @test
    def there_is_a_SSL_LOGIN_BASE_URL_config_option_containing_the_base_url_of_the_site_with_the_optional_no_ca_config(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL is not None)

    @test
    def there_is_a_BASE_URL_config_option_containing_the_plain_ssl_base_url(self):
        "where no certificate is asked"
        self.assertTrue(Config.BASE_URL is not None)

    @test
    def there_is_a_SSL_LOGOUT_URL_config_option_pointing_to_a_location_which_is_set_up_with_SSLVerifyClient_require_and_SSLVerifyDepth_0_within_SSL_LOGIN_BASE_URL(self):
        self.assertTrue(Config.SSL_LOGIN_BASE_URL in Config.SSL_LOGOUT_URL)

    @test
    def there_is_a_START_URL_config_option_which_contains_the_starting_point_useable_for_unregistered_and_or_not_logged_in_user(self):
        self.assertTrue(Config.BASE_URL in Config.START_URL)

    @test
    def you_can_login_using_a_registered_ssl_cert(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        self.assertTrue(CREDENTIAL_REPRESENTATION in
            self.getResponseText(resp))

    @test
    def ssl_login_sets_csrf_cookie(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        self.assertTrue(cookieParts.has_key('csrf'))

    @test
    def login_cookie_have_path_set_to_root(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        self.assertEquals(cookieParts['Path'], '/')

    @test
    def login_cookie_have_domain_set_to_COOKIE_DOMAIN(self):
        resp = self.createUserAndLoginWithCert()
        cookieParts = self.getCookieParts(resp)
        cookieDomain = self.controller.app.config.get('COOKIE_DOMAIN')
        self.assertEquals(cookieParts['Domain'], cookieDomain)

    @test
    def with_cert_login_you_get_actually_logged_in(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        body = self.getResponseText(resp)
        self.assertTrue(CREDENTIAL_REPRESENTATION in
            body)
        resp = self.showUserByCurrentUser('me')
        self.assertEqual(200, resp.status_code)

    @test
    def you_cannot_login_using_an_unregistered_ssl_cert_without_email(self):
        certAttr = self.getCertAttributes()
        self.assertReportedError(
            self.sslLoginWithCert, [certAttr.cert], 403, ["You have to register first"])

    @test
    def you_cannot_login_without_a_cert(self):
        self.assertReportedError(
            self.controller.do_ssl_login, [], 403, ["No certificate given"])

    @test
    def empty_certstring_gives_error(self):
        self.assertReportedError(
            self.sslLoginWithCert, [''], 403, ["No certificate given"])

    @test
    def junk_certstring_gives_error(self):
        self.assertReportedError(
            self.sslLoginWithCert, ['junk'], 400, ["error in cert", "junk"])

    @test
    def ssl_login_is_cors_enabled(self):
        resp = self.createUserAndLoginWithCert()
        self.assertEquals(resp.status_code, 200)
        self.assertEqual(resp.headers['Access-Control-Allow-Origin'], "*")

    @test
    def you_can_register_and_login_using_an_unregistered_ssl_cert_with_email(self):
        certAttr = self.getCertAttributes()
        params=dict(email="certuser@example.com")
        url = Config.BASE_URL + "?" + urlencode(params)
        self.controller.interface.set_request_context(url)
        self.controller.mail = FakeMail()
        resp = self.sslLoginWithCert(certAttr.cert)
        cred = Credential.get("certificate", certAttr.identifier)
        self.deleteUser(cred.user)
        self.assertEquals(resp.status_code, 200)
        responseText = self.getResponseText(resp)
        self.assertTrue(CREDENTIAL_REPRESENTATION in
            responseText)
        self.assertTrue('{"credentialType": "emailcheck", "identifier":' in
            responseText)
