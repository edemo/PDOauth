
from test import config
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from pdoauth.forms import credErr
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.CSRFMixin import CSRFMixin
from test.helpers.CryptoTestUtil import SPKAC

class CredentialIntegrationTest(IntegrationTest, UserTesting, CSRFMixin):
    def setUp(self):
        self.setupRandom()
        self.user = self.createUserWithCredentials().user
        self.cred=Credential.get('password', self.userCreationUserid)

    @test
    def credential_can_be_retrieved_by_type_and_identifier(self):
        self.assertEquals(self.cred.user, self.user)

    @test
    def a_logged_in_user_can_add_credential(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": "user_{0}".format(self.randString),
                "secret": "secret is {0}".format(self.mkRandomPassword())
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(200, resp.status_code)

    @test
    def a_not_logged_in_user_cannot_add_credential(self):
        with app.test_client() as client:
            self.setupRandom()
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": "user_{0}".format(self.randString),
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(403, resp.status_code)

    @test
    def the_added_credential_should_contain_credentialType(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "identifier": username,
                "secret": "secret is {0}".format(self.mkRandomPassword())
            }
            uri = config.BASE_URL + "/v1/add_credential"
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is None)
            self.assertCredentialErrorresponse(resp)

    @test
    def the_added_credential_should_contain_valid_credentialType(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "invalid",
                "identifier": username,
                "secret": "secret is {0}".format(self.mkRandomPassword())
            }
            uri = config.BASE_URL + "/v1/add_credential"
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is None)
            self.assertCredentialErrorresponse(resp)

    @test
    def the_added_credential_should_contain_identifier(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "secret": "secret is {0}".format(self.mkRandomPassword())
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_valid_identifier(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": "aaa",
                "secret": "secret is {0}".format(self.mkRandomPassword())
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_secret(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": username,
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long.", "secret: password should contain lowercase", "secret: password should contain uppercase", "secret: password should contain digit"]}',
                 self.getResponseText(resp))

    @test
    def the_password_should_be_at_least_8_characters_long(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": username,
                "secret": "sH0rt"
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long."]}', self.getResponseText(resp))

    @test
    def the_password_should_contain_lowercase_letters(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": username,
                "secret": "THIS P4SSWORD IS UPPERCASE"
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: password should contain lowercase"]}', self.getResponseText(resp))

    @test
    def the_password_should_contain_uppercase_letters(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": username,
                "secret": "th1s p4ssw0rd 15 10w3rc453"
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: password should contain uppercase"]}', self.getResponseText(resp))

    @test
    def cannot_add_an_already_existing_identifier(self):
        with app.test_client() as client:
            self.login(client)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "password",
                "identifier": self.userCreationUserid,
                "secret": self.mkRandomPassword()
            }
            uri = config.BASE_URL + "/v1/add_credential"
            resp = client.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: There is already a user with that username"]}', self.getResponseText(resp))

    @test
    def a_credential_can_be_deleted(self):
        with app.test_client() as client:
            self.login(client)
            user = User.getByEmail(self.userCreationEmail)
            credId = self.randString
            Credential.new(user, "facebook", credId, "testsecret")
            self.assertTrue(Credential.get("facebook", credId))
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "facebook",
                "identifier": credId,
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(200, resp.status_code)
            self.assertEqual('{"message": "credential removed"}', self.getResponseText(resp))

    @test
    def the_credential_is_actually_deleted(self):
        with app.test_client() as client:
            self.login(client)
            user = User.getByEmail(self.userCreationEmail)
            credId = self.randString
            Credential.new(user, "facebook", credId, "testsecret")
            self.assertTrue(Credential.get("facebook", credId))
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "facebook",
                "identifier": credId,
            }
            client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertFalse(Credential.get("facebook", credId))

    @test
    def you_can_delete_certificate_credential(self):
        with app.test_client() as client:
            self.login(client)
            user = User.getByEmail(self.userCreationEmail)
            data = dict(email=self.userCreationEmail, pubkey=SPKAC)
            client.post(config.BASE_URL + "/v1/keygen", data=data)
            certCredential = Credential.getByUser(user, 'certificate')
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "certificate",
                "identifier": certCredential.identifier,
            }
            client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertFalse(Credential.get("certificate", certCredential.identifier))

    @test
    def you_should_give_the_credentialType_for_credential_deletion(self):
        with app.test_client() as client:
            self.login(client)
            credId = self.randString
            data = {
                "csrf_token": self.getCSRF(client),
                "identifier": credId,
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(400, resp.status_code)
            self.assertCredentialErrorresponse(resp)

    @test
    def you_should_give_valid_credentialType_for_credential_deletion(self):
        with app.test_client() as client:
            self.login(client)
            credId = self.randString
            data = {
                "csrf_token": self.getCSRF(client),
                "identifier": credId,
                "credentialType": "test",
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(400, resp.status_code)
            self.assertCredentialErrorresponse(resp)

    @test
    def you_should_give_the_identifier_for_credential_deletion(self):
        with app.test_client() as client:
            self.login(client)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "facebook",
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    @test
    def you_should_give_valid_identifier_for_credential_deletion(self):
        with app.test_client() as client:
            self.login(client)
            user = User.getByEmail(self.userCreationEmail)
            credId = self.randString
            Credential.new(user, "facebook", credId, "testsecret")
            self.assertTrue(Credential.get("facebook", credId))
            data = {
                "csrf_token": self.getCSRF(client),
                "identifier": credId+"no",
                "credentialType": "facebook",
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(404, resp.status_code)
            self.assertEqual('{"errors": ["No such credential"]}', self.getResponseText(resp))
