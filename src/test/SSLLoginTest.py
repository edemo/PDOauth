from pdoauth.models.Credential import Credential
from urllib import urlencode
from test.helpers.todeprecate.UserTesting import UserTesting
from test.helpers.PDUnitTest import PDUnitTest, test

from test.config import Config
from pdoauth.ReportedError import ReportedError

class SSLLoginTest(PDUnitTest, UserTesting):

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

    def _sslLoginWithCert(self, cert):
        self.controller._testdata.environ = dict(SSL_CLIENT_CERT=cert)
        resp = self.controller._do_ssl_login()
        return resp

    @test
    def you_can_login_using_a_registered_ssl_cert(self):
        identifier, digest, cert = self.getCertAttributes()
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        resp = self._sslLoginWithCert(cert)
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            self.getResponseText(resp))
        cred.rm()

    @test
    def with_cert_login_you_get_actually_logged_in(self):
        identifier, digest, cert = self.getCertAttributes()
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        resp = self._sslLoginWithCert(cert)
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            self.getResponseText(resp))
        resp = self.controller._do_show_user('me')
        self.assertEqual(200, resp.status_code)
        cred.rm()

    @test
    def you_cannot_login_using_an_unregistered_ssl_cert_without_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        with self.assertRaises(ReportedError) as e:
            self._sslLoginWithCert(cert)
        self.assertEquals(e.exception.status, 403)
        self.assertEqual(["You have to register first"], e.exception.descriptor)

    @test
    def you_cannot_login_without_a_cert(self):
        with self.assertRaises(ReportedError) as e:
            self.controller._do_ssl_login()
        self.assertEquals(e.exception.status, 403)
        self.assertEqual(["No certificate given"], e.exception.descriptor)

    @test
    def empty_certstring_gives_error(self):
        with self.assertRaises(ReportedError) as e:
            self._sslLoginWithCert('')
        self.assertEquals(e.exception.status, 403)
        self.assertEqual(["No certificate given"], e.exception.descriptor)

    @test
    def junk_certstring_gives_error(self):
        with self.assertRaises(ReportedError) as e:
            self._sslLoginWithCert('junk')
        self.assertEquals(e.exception.status, 400)
        self.assertEqual(["error in cert", "junk"], e.exception.descriptor)

    @test
    def ssl_login_is_cors_enabled(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        resp = self._sslLoginWithCert(cert)
        self.assertEquals(resp.status_code, 200)
        self.assertEqual(resp.headers['Access-Control-Allow-Origin'], "*")
        cred.rm()

    @test
    def you_can_register_and_login_using_an_unregistered_ssl_cert_with_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        params=dict(email="certuser@example.com")
        self.controller._testdata.request_url = Config.BASE_URL+"?"+urlencode(params)
        resp = self._sslLoginWithCert(cert)
        cred = Credential.get("certificate", identifier)
        self.deleteUser(cred.user)
        self.assertEquals(resp.status_code, 200)
        responseText = self.getResponseText(resp)
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            responseText)
        self.assertTrue('{"credentialType": "emailcheck", "identifier":' in
            responseText)

    @test
    def you_cannot_ssl_login_without_a_cert(self):
        with self.assertRaises(ReportedError) as e:
            self.controller._do_ssl_login()
            self.assertEquals(e.exception.status, 403)
            self.assertEqual('{"errors": ["No certificate given"]}', e.exception.descriptor)
