from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from OpenSSL import crypto

class SSLLoginTest(Fixture, UserTesting):

    @test
    def you_can_login_using_a_registered_ssl_cert(self):
        certFile = open("src/integrationtest/client.crt")
        cert = certFile.read()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName
        identifier="{0}/{1}".format(
            digest,
            cn
        )
        user = self.createUserWithCredentials()
        secret = digest
        cred = Credential.new(user, "certificate", identifier, secret)
        certFile.close()
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login", environ_base=environ_base)
            self.assertEquals(resp.status_code, 200)
            self.assertEqual('{"message": "You are logged in"}', self.getResponseText(resp))
        cred.rm()

    @test
    def you_cannot_login_using_an_uregistered_ssl_cert(self):
        certFile = open("src/integrationtest/client.crt")
        cert = certFile.read()
        certFile.close()
        environ_base = dict(SSL_CLIENT_CERT=cert)
        with app.test_client() as c:
            resp = c.get("/ssl_login", environ_base=environ_base)
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["You have to register first"]}', self.getResponseText(resp))

    @test
    def you_cannot_ssl_login_without_a_cert(self):
        with app.test_client() as c:
            resp = c.get("/ssl_login")
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["No certificate given"]}', self.getResponseText(resp))
