from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
import time
from uuid import uuid4
from test.helpers.EmailUtil import EmailUtil
from pdoauth.models.Application import Application
from pdoauth.models.AppMap import AppMap

class DeregisterTest(PDUnitTest, EmailUtil):
    addAppMapToUser=False

    def _doDeregister(self):
        data = dict(csrf_token=self.controller.getCSRF())
        resp = self.controller.doDeregister(FakeForm(data))
        return resp

    def _assureHaveCredentialsAndAssurances(self, user):
        creds = Credential.getByUser(user)
        self.assertTrue(len(creds) > 0)
        assurances = Assurance.getByUser(user)
        self.assertTrue(len(assurances) > 0)

    def _loginAndDeregister(self):
        self.createLoggedInUser()
        user = self.cred.user
        Assurance.new(user, "test", user)
        self._assureHaveCredentialsAndAssurances(user)
        resp = self._doDeregister()
        return resp

    
    def test_you_can_deregister_with_csrf(self):
        resp = self._loginAndDeregister()
        self.assertEqual(resp.status_code, 200)

    
    def test_calling_do_deregister_sends_deregistration_email(self):
        self._loginAndDeregister()
        outbox = self.controller.mail.outbox
        self.assertEqual(len(outbox), 1)

    def _getDeregistrationSecret(self):
        self._loginAndDeregister()
        user = self.cred.user
        if self.addAppMapToUser==True:
            app = Application.query.first()  # @UndefinedVariable
            AppMap.new(app, user)
        deregistrationCredential = Credential.getByUser(user, 'deregister')
        secret = deregistrationCredential.secret
        return secret

    
    def test_deregistration_email_contains_deregistration_secret(self):
        secret = self._getDeregistrationSecret()
        mail = self.controller.mail.outbox[0]
        self.assertEmailContains(secret, mail)

    
    def test_deregistration_email_contains_DEREGISTRATION_URL(self):
        self._loginAndDeregister()
        mail = self.controller.mail.outbox[0]
        deregistrationUrl = self.controller.getConfig('DEREGISTRATION_URL')
        self.assertEmailContains(deregistrationUrl, mail)

    
    def test_deregistration_doit_needs_deregistration_secret(self):
        emptyForm = FakeForm(dict(deregister_secret=None))
        self.assertReportedError(self.controller.doDeregistrationDoit, [emptyForm], 400, ["secret is needed for deregistration_doit"])

    def _doDeregistrationDoit(self, overwriteSecret=None):
        secret = self._getDeregistrationSecret()
        if overwriteSecret is not None:
            secret = overwriteSecret
        resp = self.controller.doDeregistrationDoit(FakeForm(dict(deregister_secret=secret)))
        return resp

            
    def test_deregistration_doit_works_with_right_secret_and_csrf(self):
        resp = self._doDeregistrationDoit()
        self.assertEqual(resp.status_code, 200)
        msg = self.fromJson(resp)
        self.assertEqual(msg['message'], 'you are deregistered')

            
    def test_deregistration_doit_does_not_work_with_bad_secret(self):
        self.assertReportedError(self._doDeregistrationDoit, ['junk'], 400, ['bad deregistration secret'])

    
    def test_your_credentials_are_deleted_in_deregistration(self):
        self._doDeregistrationDoit()
        user = User.getByEmail(self.userCreationEmail)
        creds = Credential.getByUser(user)
        self.assertTrue(len(creds) == 0)
            
    
    def test_your_assurances_are_deleted_in_deregistration(self):
        self._doDeregistrationDoit()
        user = User.getByEmail(self.userCreationEmail)
        assurances = Assurance.getByUser(user)
        self.assertTrue(len(assurances) == 0)

    
    def test_your_user_is_deleted_in_deregistration(self):
        self._doDeregistrationDoit()
        user = User.getByEmail(self.userCreationEmail)
        self.assertTrue(user is None)

    
    def test_expired_deregistration_certificates_are_deleted_in_deregistration_initiation(self):
        for someone in User.query.all()[:5]:  # @UndefinedVariable
            Credential.new(someone, 'deregister', str(time.time()-1)+":"+uuid4().hex, uuid4().hex)
        self.assertTrue(self.countExpiredCreds('deregister')>=5)
        self._doDeregistrationDoit()
        self.assertTrue(self.countExpiredCreds('deregister')==0)

    
    def test_your_user_with_appmap_is_deleted_in_deregistration(self):
        self.addAppMapToUser=True
        self._doDeregistrationDoit()
        user = User.getByEmail(self.userCreationEmail)
        self.assertTrue(user is None)
