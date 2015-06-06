from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from OpenSSL import crypto
from pdoauth.models.User import User
from test.helpers.todeprecate.UserTesting import UserTesting

spkac = """MIICSTCCATEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDt66ujL7Qi
gKPRoJzI7cdMFgxoNE7u5aKhAMLC7EE9Npn7Ig1Y6G5NIfjdWZy+Ryrw3/HdYRsS
9bL2LZb+w17lnrR8jv6kMRPuqw+tPGZMdri/QF6IZnbSa77zTLHB/z0Ffx/wgicX
Yp/XPJLwM0iNzanjnFoG1dlaQ8PL5lHbuHnorCpV9TbAzGkzofm059RxoHT8bes0
D4t4JzQaSKhpGf+w2SD2TlnxE9My1IK/q3UrgreBJ4Wn6CG0G6sTL2gw60oFr0Go
1n8ESRgXkt4DyiW5rjcj087WdxYYHYtJLv3czwSytvUeFfWl2EAtXJnH4AWuDS7S
iyT38IPwk8tZAgMBAAEWCTEyMzQ1Njc4OTANBgkqhkiG9w0BAQQFAAOCAQEA0kt4
sDLvT3ho/pxXIT14OcCtMxRvTq5CuEKrMICjnrOIwWcWLtjNBOTRW0cobEsn970k
vNjkzH/BnEzXwCqLPN0s6ctXHyTC8Y+528iFCw7R4nvMgAevqI4x1CNWB+/l0Hl5
0507mHjMJWSjqsW2RlQb/mp4S1rN8+VDja5hUCxRKc1/9omUht5EcygciMsKC79k
N8v6i3mEYWeRnsIXDfWpWZoejEm3cdlCr2sstFQ4GIzTw/KIHnEnkCOZWz8uQVIE
FiFJjirn+7QTlDjctU89Y4OqX2pufBxULSLMVnc8aM1/vXUDwtQKFuS1hr2DrUbb
JA3SM6HtjlWWGuocNw=="""

class KeygenTest(Fixture, UserTesting):

    def _getCertId(self, cert):
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName.encode('raw_unicode_escape').decode('utf-8')
        identifier = u"{0}/{1}".format(digest, cn)
        return identifier, cn

    def setUp(self):
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
            cred.rm()

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
