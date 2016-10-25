# -*- coding: UTF-8 -*-
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance, emailVerification
from flask_login import logout_user
from integrationtest import config
import time
from integrationtest.helpers.UserTesting import UserTesting
from test.helpers.EmailUtil import EmailUtil

app.extensions["mail"].suppress = True

class EmailVerificationTests(IntegrationTest, UserTesting, EmailUtil):

    
    def test_email_validation_gives_emailverification_assurance(self):
        self.setupRandom()
        with app.test_client():
            email = self.registerAndObtainValidationUri()
            self.assertTrue(self.validateUri.startswith(config.BASE_URL + "/v1/verify_email"))
        with app.test_client() as client:
            user = User.getByEmail(email)
            creds = Credential.getByUser(user)
            assurances = Assurance.getByUser(user)
            self.assertTrue(emailVerification not in assurances)
            resp = client.get(self.validateUri)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(user.email, email)
            newcreds = Credential.getByUser(user)
            self.assertEqual(len(creds) - 1 , len(newcreds))
            assurances = Assurance.getByUser(user)
            self.assertTrue(assurances[emailVerification] is not None)
            user.rm()

    def registerAndObtainValidationUri(self):
        with app.test_client() as client:
            resp = self.register(client)
            email = self.registeredEmail
            logout_user()
            self.assertUserResponse(resp)
            self.validateUri = self.getValidateUri()
        return email

    
    def test_email_verification_after_expiry_will_fail(self):
        self.setupRandom()
        email = self.registerAndObtainValidationUri()
        with app.test_client() as client:
            user = User.getByEmail(email)
            creds = Credential.getByUser(user)
            for cred in creds:
                if cred.credentialType == 'emailcheck':
                    cred.identifier = str(time.time()- 1)
            resp = client.get(self.validateUri)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["expired token"]}', self.getResponseText(resp))

    
    def test_bad_email_uri_signals_error(self):
        with app.test_client() as client:
            resp = client.get(config.BASE_URL + "/v1/verify_email/badkey")
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(self.getResponseText(resp),'{"errors": ["unknown token"]}')

    
    def test_email_validation_email_can_be_resent(self):
        with app.test_client() as client:
            self.login(client)
            client.get(config.BASE_URL + "/v1/send_verify_email")
            user=User.get(self.userid)
            self.assertEqual(self.userCreationEmail, Credential.getByUser(user, "emailcheck").user.email)
