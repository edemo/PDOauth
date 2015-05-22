# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
import re
from pdoauth.models.Assurance import Assurance, emailVerification
from test.TestUtil import UserTesting
from flask_login import logout_user
import config
import time

app.extensions["mail"].suppress = True

class EmailVerificationTests(Fixture, UserTesting):

    @test
    def email_validation_gives_emailverification_assurance(self):
        self.setupRandom()
        with app.test_client() as c:
            resp, outbox = self.register(c)
            email = self.registered_email
            logout_user()
            self.assertUserResponse(resp)
            self.validateUri=re.search('href="([^"]*)',outbox[0].body).group(1)
            self.assertTrue(self.validateUri.startswith(config.base_url + "/v1/verify_email/"))
        with app.test_client() as c:
            user = User.getByEmail(email)
            creds = Credential.getByUser(user)
            assurances = Assurance.getByUser(user)
            self.assertTrue(assurances.has_key(emailVerification) is False)
            resp = c.get(self.validateUri)
            self.assertEqual(user.email, email)
            newcreds = Credential.getByUser(user)
            self.assertEquals(len(creds) - 1 , len(newcreds))
            assurances = Assurance.getByUser(user)
            self.assertTrue(assurances[emailVerification] is not None)
            user.rm()

    @test
    def email_verification_after_expiry_will_fail(self):
        self.setupRandom()
        with app.test_client() as c:
            resp, outbox = self.register(c)  # @UnusedVariable
            email = self.registered_email
            logout_user()
            self.validateUri=re.search('href="([^"]*)',outbox[0].body).group(1)
        with app.test_client() as c:
            user = User.getByEmail(email)
            creds = Credential.getByUser(user)
            for cred in creds:
                if cred.credentialType == 'emailcheck':
                    cred.identifier = unicode(time.time()- 1)
            resp = c.get(self.validateUri)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["expired token"]}', self.getResponseText(resp))

    @test
    def bad_email_uri_signals_error(self):
        with app.test_client() as c:
            resp = c.get(config.base_url + "/v1/verify_email/badkey")
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(self.getResponseText(resp),'{"errors": ["unknown token"]}')

