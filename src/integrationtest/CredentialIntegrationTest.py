
from test import config
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.CSRFMixin import CSRFMixin

class CredentialIntegrationTest(IntegrationTest, UserTesting, CSRFMixin):
    def setUp(self):
        self.setupRandom()
        self.user = self.createUserWithCredentials().user
        self.cred=Credential.get('password', self.userCreationUserid)

    
    def test_credential_can_be_retrieved_by_type_and_identifier(self):
        self.assertEqual(self.cred.user, self.user)

    def addPasswordCredential(self, client, username=None, credentialtype=None, password=None, nofield=None):
        if username is None:
            username = "user_{0}".format(self.randString)
        if credentialtype is None:
            credentialtype = "password"
        if password is None:
            password = "secret is {0}".format(self.mkRandomPassword())
        data = {"csrf_token":self.getCSRF(client), 
            "credentialType":credentialtype, 
            "identifier":username, 
            "password":password}
        if nofield is not None:
            data.pop(nofield)
        uri = config.BASE_URL + "/v1/add_credential"
        resp = client.post(uri, data=data)
        return resp

    
    def test_a_logged_in_user_can_add_credential(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            resp = self.addPasswordCredential(client)
            self.assertEqual(200, resp.status_code)

    
    def test_a_not_logged_in_user_cannot_add_credential(self):
        with app.test_client() as client:
            self.setupRandom()
            resp = self.addPasswordCredential(client)
            self.assertEqual(403, resp.status_code)

    
    def test_the_added_credential_should_contain_credentialType(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = self.addPasswordCredential(client, username=username, nofield="credentialType")
            self.assertEqual(400, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is None)
            self.assertCredentialErrorresponse(resp)

    
    def test_the_added_credential_should_contain_valid_credentialType(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client, credentialtype="invalid")
            self.assertCredentialErrorresponse(resp)

    
    def test_the_added_credential_should_contain_identifier(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            resp = self.addPasswordCredential(client,nofield="identifier")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    
    def test_the_added_credential_should_contain_valid_identifier(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client,username="aaa")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    
    def test_the_added_credential_should_contain_secret(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client,nofield="password")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["password: Field must be at least 8 characters long.", "password: password should contain lowercase", "password: password should contain uppercase", "password: password should contain digit"]}',
                 self.getResponseText(resp))

    
    def test_the_password_should_be_at_least_8_characters_long(self):
        with app.test_client() as client:
            self.login(client)
            self.setupRandom()
            resp = self.addPasswordCredential(client,password="sH0rt")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["password: Field must be at least 8 characters long."]}', self.getResponseText(resp))

    
    def test_the_password_should_contain_lowercase_letters(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client,password="THIS P4SSWORD IS UPPERCASE")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["password: password should contain lowercase"]}', self.getResponseText(resp))

    
    def test_the_password_should_contain_uppercase_letters(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client,password="th1s p4ssw0rd 15 10w3rc453")
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["password: password should contain uppercase"]}', self.getResponseText(resp))

    
    def test_cannot_add_an_already_existing_identifier(self):
        with app.test_client() as client:
            self.login(client)
            resp = self.addPasswordCredential(client,username=self.userCreationUserid)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: There is already a user with that username"]}', self.getResponseText(resp))

    
    def test_a_credential_can_be_deleted(self):
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

    
    def test_the_credential_is_actually_deleted(self):
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

    
    def test_you_should_give_the_credentialType_for_credential_deletion(self):
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

    
    def test_you_should_give_valid_credentialType_for_credential_deletion(self):
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

    
    def test_you_should_give_the_identifier_for_credential_deletion(self):
        with app.test_client() as client:
            self.login(client)
            data = {
                "csrf_token": self.getCSRF(client),
                "credentialType": "facebook",
            }
            resp = client.post(config.BASE_URL + "/v1/remove_credential", data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 250 characters long."]}', self.getResponseText(resp))

    
    def test_you_should_give_valid_identifier_for_credential_deletion(self):
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
