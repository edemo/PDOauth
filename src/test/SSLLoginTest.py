from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from urllib import urlencode

class SSLLoginTest(Fixture, UserTesting):

    @test
    def there_is_a_SSL_LOGIN_BASE_URL_config_option_containing_the_base_url_of_the_site_with_the_optional_no_ca_config(self):
        self.assertTrue(app.config.get('SSL_LOGIN_BASE_URL') is not None)

    @test
    def there_is_a_BASE_URL_config_option_containing_the_plain_ssl_base_url(self):
        "where no certificate is asked"
        self.assertTrue(app.config.get('BASE_URL') is not None)

    @test
    def there_is_a_SSL_LOGOUT_URL_config_option_pointing_to_a_location_which_is_set_up_with_SSLVerifyClient_require_and_SSLVerifyDepth_0_within_SSL_LOGIN_BASE_URL(self):
        self.assertTrue(app.config.get('SSL_LOGIN_BASE_URL') in app.config.get('SSL_LOGOUT_URL'))
    
    @test
    def there_is_a_START_URL_config_option_which_contains_the_starting_point_useable_for_unregistered_and_or_not_logged_in_user(self):
        self.assertTrue(app.config.get('BASE_URL') in app.config.get('START_URL'))
                
    @test
    def you_can_login_using_a_registered_ssl_cert(self):
        identifier, digest, cert = self.getCertAttributes()
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login", environ_base=environ_base)
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
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login", environ_base=environ_base)
            self.assertEquals(resp.status_code, 200)
            self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
                self.getResponseText(resp))
            resp = c.get("/v1/users/me")
            self.assertEqual(200, resp.status_code)
        cred.rm()

    @test
    def you_cannot_login_using_an_unregistered_ssl_cert_without_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login", environ_base=environ_base)
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["You have to register first"]}', self.getResponseText(resp))

    @test
    def you_cannot_login_without_a_cert(self):
        with app.test_client() as c:
            resp = c.get("/ssl_login")
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["No certificate given"]}', self.getResponseText(resp))

    @test
    def empty_certstring_gives_error(self):
        environ_base = dict(SSL_CLIENT_CERT='')
        with app.test_client() as c:
            resp = c.get("/ssl_login",environ_base=environ_base)
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["No certificate given"]}', self.getResponseText(resp))

    @test
    def junk_certstring_gives_error(self):
        environ_base = dict(SSL_CLIENT_CERT='junk')
        with app.test_client() as c:
            resp = c.get("/ssl_login",environ_base=environ_base)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["error in cert", "junk"]}', self.getResponseText(resp))

    @test
    def ssl_login_is_cors_enabled(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login",environ_base=environ_base)
            self.assertEquals(resp.status_code, 200)
            self.assertEqual(resp.headers['Access-Control-Allow-Origin'], "*")
        cred.rm()

    @test
    def you_can_register_and_login_using_an_unregistered_ssl_cert_with_email(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        environ_base = dict(SSL_CLIENT_CERT=cert)
        params=dict(email="certuser@example.com")
        queryString = urlencode(params)
        with app.test_client() as c:
            resp = c.get("/ssl_login", query_string=queryString,environ_base=environ_base)
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
        with app.test_client() as c:
            resp = c.get("/ssl_login")
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["No certificate given"]}', self.getResponseText(resp))
