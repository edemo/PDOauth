from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from oauthlib.common import urldecode
from pdoauth.models.Credential import Credential
from OpenSSL import crypto
from pdoauth.models.User import User

class KeygenTest(Fixture, UserTesting):

    def _getCertId(self, cert):
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName.encode('raw_unicode_escape').decode('utf-8')
        identifier = u"{0}/{1}".format(digest, cn)
        return identifier, cn

    def setUp(self):
        encoded = "MIICSTCCATEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDt66ujL7Qi%0D%0AgKPRoJzI7cdMFgxoNE7u5aKhAMLC7EE9Npn7Ig1Y6G5NIfjdWZy%2BRyrw3%2FHdYRsS%0D%0A9bL2LZb%2Bw17lnrR8jv6kMRPuqw%2BtPGZMdri%2FQF6IZnbSa77zTLHB%2Fz0Ffx%2FwgicX%0D%0AYp%2FXPJLwM0iNzanjnFoG1dlaQ8PL5lHbuHnorCpV9TbAzGkzofm059RxoHT8bes0%0D%0AD4t4JzQaSKhpGf%2Bw2SD2TlnxE9My1IK%2Fq3UrgreBJ4Wn6CG0G6sTL2gw60oFr0Go%0D%0A1n8ESRgXkt4DyiW5rjcj087WdxYYHYtJLv3czwSytvUeFfWl2EAtXJnH4AWuDS7S%0D%0AiyT38IPwk8tZAgMBAAEWCTEyMzQ1Njc4OTANBgkqhkiG9w0BAQQFAAOCAQEA0kt4%0D%0AsDLvT3ho%2FpxXIT14OcCtMxRvTq5CuEKrMICjnrOIwWcWLtjNBOTRW0cobEsn970k%0D%0AvNjkzH%2FBnEzXwCqLPN0s6ctXHyTC8Y%2B528iFCw7R4nvMgAevqI4x1CNWB%2B%2Fl0Hl5%0D%0A0507mHjMJWSjqsW2RlQb%2Fmp4S1rN8%2BVDja5hUCxRKc1%2F9omUht5EcygciMsKC79k%0D%0AN8v6i3mEYWeRnsIXDfWpWZoejEm3cdlCr2sstFQ4GIzTw%2FKIHnEnkCOZWz8uQVIE%0D%0AFiFJjirn%2B7QTlDjctU89Y4OqX2pufBxULSLMVnc8aM1%2FvXUDwtQKFuS1hr2DrUbb%0D%0AJA3SM6HtjlWWGuocNw%3D%3D"
        spkac = urldecode(encoded)[0][0]
        self.setupUserCreationData()
        self.certemail=self.usercreation_email
        self.data = dict(
            pubkey=spkac,
            email=self.usercreation_email
        )
        self.headers = {
            "Content-Type":"application/x-www-form-urlencoded"}

    @test
    def with_keygen_you_get_back_a_certificate(self):
        with app.test_client() as c:
            resp = c.post("/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, cn = self._getCertId(cert)  # @UnusedVariable

    @test
    def with_keygen_you_get_back_a_certificate_for_the_given_email(self):
        with app.test_client() as c:
            resp = c.post("/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, cn = self._getCertId(cert)
            self.assertEqual(self.usercreation_email,cn)
            cred = Credential.get("certificate", identifier)
            self.assertEqual(None, cred)

    @test
    def if_the_user_is_logged_in__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.post("/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, cn = self._getCertId(cert)  # @UnusedVariable
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.usercreation_email)
            self.assertTrue(self.usercreation_email != cn)
            self.deleteUser(cred.user)

    @test
    def if_createUser_is_set__a_new_user_is_created_with_the_cert_and_logged_in(self):
        with app.test_client() as c:
            self.data['createUser']=True
            self.assertEqual(None, User.getByEmail(self.usercreation_email))
            resp = c.post("/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, cn = self._getCertId(cert)  # @UnusedVariable
            resp2 = c.get("/v1/users/me")
            self.assertEqual(200, resp2.status_code)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEquals(cred.user.email, self.usercreation_email)
            self.deleteUser(cred.user)

    @test
    def if_the_user_is_logged_in_and_createUser_is_set__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as c:
            self.login(c)
            self.data['createUser']=True
            resp = c.post("/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getResponseText(resp)
            identifier, cn = self._getCertId(cert)  # @UnusedVariable
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.usercreation_email)
            self.assertTrue(self.usercreation_email != cn)
            self.deleteUser(cred.user)
