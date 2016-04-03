from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from integrationtest.helpers.UserTesting import UserTesting
from test.helpers.CryptoTestUtil import SPKAC

wrong_pubkey = "MIICrjCCAZgCAQAwOzE5MAkGA1UEBhMCUlUwLAYDVQQDDCVTaW1wbGUgdGVzdCAo0L/RgNC+0YHRgtC+0Lkg0YLQtdGB0YIpMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuuQlljmrP1oWkbnOvL1FTZFWlnEtgHd/mY8bB/z1raqILqhQXNbZJ/MKd23xq/g3RDxY74rAj4pTBDkOWud5k0OoG0UpeHC1NsPOBpq37m6hCcsiash1ss64S8T2Tj6Iu7ZuFZkq41dFm4C9SpOligLfjKAVaMggrSD4XwoptYjTZrusLgrZP5EqMPiU/kDyOzpImz1CXglrpSE2X1MxPNVyr6Dokj/eOLqY6GXrG1GFbmGyrIGFD6ZFPnyofLQT6Yu6y65R0v4cdP+qmbuMXJBqaB0LANEfQFMUlYHeyXvIbgLi39t70z5tsOkDChK4bU/DaR5duIpCmQ0S0FFjjwIDAQABoDAwLgYJKoZIhvcNAQkOMSEwHzAdBgNVHQ4EFgQUmDO/8Sjqv0I2gTNfxB2A7Dlb0ZkwCwYJKoZIhvcNAQENA4IBAQAbQ3x3L8bWXYKBX3QwPepNCLi4i737BU+ufOL0snxgTjkOyyRrMS+g/NoOINfvvDft8uMgkIUT0Y/kP8Ir/V2++EYsnpxK2T2itziVRRRqfrSIzU2EGmPyLGt12b12jCB1Lyq/AyENs1AE49rcagEw8nGaWQXPm9U7WnlupioylAH5YrdEcJVieTUNclMPxLLDXNbDUG72DD6dZPmoVfDqbgSDfsKoB/S6Nj8AMAEtVB7ZMxudfGervcr5ej3LTaYpJ0W0uPlmmvwzxLD3ttm4kt+saatVWOcbXWUZlfSgk+PlEFXYD3+0RmeaqYMgjoU11jVMN/lCsR6UspIaYHHm"

class KeygenTest(PDUnitTest, UserTesting):

    def setUp(self):
        self.setupUserCreationData()
        self.certemail=self.userCreationEmail
        self.data = dict(
            pubkey=SPKAC,
            email=self.userCreationEmail
        )
        self.headers = {
            "Content-Type":"application/x-www-form-urlencoded"}
        PDUnitTest.setUp(self)

    @test
    def wrong_data_results_in_error_message(self):
        data=dict(
            pubkey=wrong_pubkey,
            email="valami@drezina.hu"
            )
        with app.test_client() as client:
            resp = client.post("/v1/keygen", data=data, headers=self.headers)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": "error in cert"}',self.getResponseText(resp))
        
    @test
    def with_keygen_you_get_back_a_certificate(self):
        with app.test_client() as client:
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            self.getCertFromResponse(resp)

    @test
    def with_keygen_you_get_back_a_certificate_for_the_given_email(self):
        with app.test_client() as client:
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            identifier = self.controller.getIdentifier(cert)
            self.assertEqual(self.userCreationEmail,cert.get_subject().commonName)
            cred = Credential.get("certificate", identifier)
            cred.rm()

    @test
    def if_the_user_is_logged_in__a_credential_is_added_to_the_user_for_the_cert(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            identifier = self.controller.getIdentifier(cert)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != cert.get_subject().commonName)
            self.deleteUser(cred.user)

    @test
    def if_createUser_is_set__a_new_user_is_created_with_the_cert_and_logged_in(self):
        with app.test_client() as client:
            self.data['createUser']=True
            self.assertEqual(None, User.getByEmail(self.userCreationEmail))
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
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
            resp = client.post("/v1/keygen", data=self.data, headers=self.headers)
            self.assertEquals(resp.status_code, 200)
            cert = self.getCertFromResponse(resp)
            identifier = self.controller.getIdentifier(cert)
            cred = Credential.get("certificate", identifier)
            self.assertTrue(cred)
            self.assertEqual(cred.user.email, self.userCreationEmail)
            self.assertTrue(self.userCreationEmail != cert.get_subject().commonName)
            self.deleteUser(cred.user)
