from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from integrationtest.helpers.UserTesting import UserTesting
from pdoauth.CertificateAuthority import CertificateAuthority
from test.helpers.PDUnitTest import PDUnitTest, test

pkcs10 = """
-----BEGIN CERTIFICATE REQUEST-----
MIICsTCCAZkCAQAwbDELMAkGA1UEBhMCSFUxETAPBgNVBAgMCEJ1ZGFwZXN0MSkw
JwYDVQQKDCBpbmZvcm1hdGlrdXNvayBheiBlZGVtb2tyYWNpYWVydDEfMB0GA1UE
AwwWc3NvLmVkZW1va3JhY2lhZ2VwLm9yZzCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBANqYBC5nxWCVRGv5UzfgniD9pCRbJ/9gimRl1BYOqztETIq+kL68
ZB244t/C6KHj9A5fv1zdu7xgPHXgX5bVac6ZlXJ+hByfzk5hMcOJMznNWAGX5MxN
rpbl9NjME7QWGHa6x3108rtTYfEfVFOlvsVHMXlrOjrrROUiALME5061Vrp3LyLG
BDnQARJY/6S+jd55CCtj+DVKvTXVpU/dRlnqUEysEIXqXkIgKnMDqjXwbCoPErxe
1g0c5zP5QV6sPADN/s+wYXMdIhCJwzwHTM0wJp6FcWO0PxjzdG6/Hk9fc2dAi5cK
JgXxNMVM9wffDOY28ZMevqTAl+M36p880XECAwEAAaAAMA0GCSqGSIb3DQEBCwUA
A4IBAQCO51Zcm2QghIbcau+2ljpwRU6g4KrLYyKCmzQKjN5o2E1PkXPrF1cteIaI
H2om8A1W/7Htr1S5l0qfvzceoWZhjg7At6AQTzH5CqhvlsKBZB+OCFYI2RNXnqEY
UVNQA+Knr343H+/rua2rkHRxgievxvxxmq45spU/zUmiDHeuOFuBXZ9UVdalq2VO
A6JhBGw7iqJ/5InpEYL6qf/nL8zn4yLttIHbhbXQW8CZ+toS27ciw7CyExh+/s66
vGUdDDjY7MEmeGvbcQW/0f2Nv7Hkcsx+uqY+JdOC8qtr/qUAee8QOYxseBrEhku8
zbkjq8HlENlyLmrTwjfPVWDXF3Gb
-----END CERTIFICATE REQUEST-----
"""



class PKCS10Test(PDUnitTest, UserTesting):
    
    def setUp(self):
        self.setupUserCreationData()
        self.certemail=self.userCreationEmail
        self.data = dict(
            pubkey=pkcs10,
            email=self.userCreationEmail
        )
        self.headers = {
            "Content-Type":"application/x-www-form-urlencoded"}
        PDUnitTest.setUp(self)
        

    @test
    def certificate_can_be_created_from_a_PKCS10(self):
        cert = self.controller.createCertFromReq(pkcs10, self.createRandomEmailAddress())
        self.assertEqual(cert.get_issuer(), CertificateAuthority.getInstance(self.controller).subject)

    @test
    def certificate_subject_is_the_email_address(self):
        emailAddress = self.createRandomEmailAddress()
        cert = self.controller.createCertFromReq(pkcs10, emailAddress)
        self.assertEqual(cert.get_subject().get_components(), [('CN',emailAddress)])

    @test

    def with_pkcs10_you_get_back_a_certificate_for_the_given_email(self):
        with app.test_client() as client:
            resp = client.post("/v1/ca/signreq", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            self.assertEqual(self.userCreationEmail, cert.get_subject().commonName)

    @test
    def if_the_user_is_logged_in__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.post("/v1/ca/signreq", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            cred = Credential.get("certificate", self.controller.getIdentifier(cert))
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != cert.get_subject().commonName)
            self.deleteUser(cred.user)

    @test
    def if_createUser_is_set__a_new_user_is_created_with_the_cert_and_logged_in(self):
        with app.test_client() as client:
            self.data['createUser']=True
            self.assertEqual(None, User.getByEmail(self.userCreationEmail))
            resp = client.post("/v1/ca/signreq", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            identifier = self.controller.getIdentifier(cert)
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
            resp = client.post("/v1/ca/signreq", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            identifier = self.controller.getIdentifier(cert)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != cert.get_subject().commonName)
            self.deleteUser(cred.user)
