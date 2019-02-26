#pylint: disable=no-member
from pdoauth.app import app
from pdoauth.models.Credential import Credential
import time
from uuid import uuid4
from pdoauth.models.User import User
from integrationtest.helpers.IntegrationTest import IntegrationTest
from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.EmailUtil import EmailUtil

app.extensions["mail"].suppress = True

class PasswordResetIntegrationTest(IntegrationTest, PDUnitTest, EmailUtil):

    def setUp(self):
        self.createUserWithCredentials()
        PDUnitTest.setUp(self)

    
    def test_have_passwordreset_uri(self):
        with app.test_client() as client:
            resp = client.get("/v1/users/{0}/passwordreset".format(self.userCreationEmail))
            self.assertEqual(resp.status_code, 200)
    
    def test_password_reset_needs_password(self):
        secret = uuid4().hex
        with app.test_client() as client:
            data = dict(secret=secret)
            resp = client.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 400)
            respData = self.fromJson(resp)
            self.assertTrue("password" in respData['errors'][0])

    
    def test_password_reset_needs_secret(self):
        password = self.mkRandomPassword()
        with app.test_client() as client:
            data = dict(password=password)
            resp = client.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 400)
            respData = self.fromJson(resp)
            self.assertTrue("secret" in respData['errors'][0])

    
    def test_password_reset_secret_have_to_be_valid(self):
        password = self.mkRandomPassword()
        secret = uuid4().hex
        with app.test_client() as client:
            data = dict(password=password, secret=secret)
            resp = client.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 404)
            respData = self.fromJson(resp)
            self.assertEqual('The secret has expired',respData['errors'][0])

    
    def test_valid_secret_is_accepted(self):
        password = self.mkRandomPassword()
        secret = uuid4().hex
        user = User.getByEmail(self.userCreationEmail)
        Credential.new(user, 'email_for_password_reset', str(time.time()+3600), secret)
        with app.test_client() as client:
            data = dict(password=password, secret=secret)
            resp = client.post("/v1/password_reset", data = data)
            self.assertEqual(resp.status_code, 200)
            respData = self.fromJson(resp)
            self.assertEqual("Password successfully changed",respData['message'])
