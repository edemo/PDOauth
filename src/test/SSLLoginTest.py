from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from urllib import urlencode

class SSLLoginTest(Fixture, UserTesting):

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
