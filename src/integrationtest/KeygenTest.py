from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from OpenSSL import crypto
from pdoauth.models.User import User
from integrationtest.helpers.UserTesting import UserTesting
from test.helpers.CryptoTestUtil import SPKAC


class KeygenTest(IntegrationTest, UserTesting):

    def _getCertId(self, cert):
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
        digest = x509.digest('sha1')
        commonName = x509.get_subject().commonName.encode('raw_unicode_escape').decode('utf-8')
        identifier = u"{0}/{1}".format(digest, commonName)
        return identifier, commonName

    def setUp(self):
        self.setupUserCreationData()
        self.certemail=self.userCreationEmail
        self.data = dict(
            pubkey=SPKAC,
            email=self.userCreationEmail
        )
        self.headers = {
            "Content-Type":"application/x-www-form-urlencoded"}

    @test
    def with_keygen_you_get_back_a_certificate(self):
        with app.test_client() as client:
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            self.assertTrue(self._getCertId(cert))

    @test
    def with_keygen_you_get_back_a_certificate_for_the_given_email(self):
        with app.test_client() as client:
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, commonName = self._getCertId(cert)
            self.assertEqual(self.userCreationEmail,commonName)
            cred = Credential.get("certificate", identifier)
            cred.rm()

    @test
    def if_the_user_is_logged_in__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, commonName = self._getCertId(cert)  # @UnusedVariable
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != commonName)
            self.deleteUser(cred.user)

    @test
    def if_createUser_is_set__a_new_user_is_created_with_the_cert_and_logged_in(self):
        with app.test_client() as client:
            self.data['createUser']=True
            self.assertEqual(None, User.getByEmail(self.userCreationEmail))
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier = self._getCertId(cert)[0]
            resp2 = client.get("/v1/users/me")
            self.assertEqual(200, resp2.status_code)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEquals(cred.user.email, self.userCreationEmail)
            self.deleteUser(cred.user)

    @test
    def if_the_user_is_logged_in_and_createUser_is_set__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as client:
            self.login(client)
            self.data['createUser']=True
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, commonName = self._getCertId(cert)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != commonName)
            self.deleteUser(cred.user)
