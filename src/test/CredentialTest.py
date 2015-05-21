from test.TestUtil import UserTesting
from twatson.unittest_annotations import Fixture, test
import config
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from Crypto.Hash.SHA256 import SHA256Hash

class CredentialTest(Fixture, UserTesting):
    def setUp(self):
        self.setupRandom()
        self.user = self.createUserWithCredentials()
        self.cred=Credential.get('password', self.usercreation_userid)

    @test
    def Credential_representation_is_readable(self):
        secretdigest=SHA256Hash(self.usercreation_password).hexdigest()
        representation = "Credential(user={0},credentialType=password,secret={1})".format(
            self.usercreation_email,
            secretdigest)
        self.assertEquals("{0}".format(self.cred),representation)
        
    @test
    def Credential_can_be_retrieved_by_type_and_identifier(self):
        self.assertEquals(self.cred.user, self.user)

    @test
    def a_logged_in_user_can_add_credential(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            data = {
                "credentialType": "password",
                "identifier": "user_{0}".format(self.randString),
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(200, resp.status_code)

    @test
    def when_a_credential_is_added_the_response_contains_user_data_which_contains_her_credentials(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "credentialType": "password",
                "identifier": username,
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            text = self.getResponseText(resp)
            self.assertTrue(username in text)

    @test
    def a_not_logged_in_user_cannot_add_credential(self):
        with app.test_client() as c:
            self.setupRandom()
            data = {
                "credentialType": "password",
                "identifier": "user_{0}".format(self.randString),
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(302, resp.status_code)

    @test
    def the_credential_is_actually_added(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "credentialType": "password",
                "identifier": username,
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = c.post(uri, data=data)
            self.assertEqual(200, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is not None)

    @test
    def the_added_credential_should_contain_credentialType(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "identifier": username,
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is None)
            self.assertEqual('{"errors": ["credentialType: Invalid value, must be one of: password, facebook."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_valid_credentialType(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "credentialType": "invalid",
                "identifier": username,
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            credBefore = Credential.get("password", username)
            self.assertTrue(credBefore is None)
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            credAfter = Credential.get("password", username)
            self.assertTrue(credAfter is None)
            self.assertEqual('{"errors": ["credentialType: Invalid value, must be one of: password, facebook."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_identifier(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            data = {
                "credentialType": "password",
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 25 characters long."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_valid_identifier(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            data = {
                "credentialType": "password",
                "identifier": "aaa",
                "secret": "secret is {0}".format(self.randString)
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: Field must be between 4 and 25 characters long."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_secret(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "credentialType": "password",
                "identifier": username,
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long."]}', self.getResponseText(resp))

    @test
    def the_added_credential_should_contain_valid_secret(self):
        with app.test_client() as c:
            self.login(c)
            self.setupRandom()
            username = "user_{0}".format(self.randString)
            data = {
                "credentialType": "password",
                "identifier": username,
                "secret": "short"
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["secret: Field must be at least 8 characters long."]}', self.getResponseText(resp))

    @test
    def cannot_add_an_already_existing_identifier(self):
        with app.test_client() as c:
            self.login(c)
            data = {
                "credentialType": "password",
                "identifier": self.usercreation_userid,
                "secret": "aaaaaaaaaaaa"
            }
            uri = config.base_url + "/v1/add_credential"
            resp = c.post(uri, data=data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["identifier: There is already a user with that username"]}', self.getResponseText(resp))
