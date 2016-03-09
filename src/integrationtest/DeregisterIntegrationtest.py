from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.app import app, mail
from integrationtest import config
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.CSRFMixin import CSRFMixin
import re
from uuid import uuid4

class DeregisterIntegrationTest(IntegrationTest, UserTesting, CSRFMixin):

    def _doDeregistration(self,token=None, nologin=None):
        otoken = token
        with app.test_client() as client:
            if nologin is None:
                self.login(client)
            self.data = dict()
            self.addDataBasedOnOptionValue('csrf_token', token, self.getCSRF(client))
            with mail.record_messages() as outbox:
                resp = client.post(config.BASE_URL + '/v1/deregister', data=self.data)
                self.outbox = outbox
            if otoken is None and nologin is None:
                msg=self.outbox[0]
                body = msg.html
                self.secret = re.search(r'deregistration_secret=([^"]*)"', body).groups()[0]
        return resp

    @test
    def you_call_deregister_to_deregister(self):
        resp = self._doDeregistration()
        self.assertEquals(resp.status_code, 200)
        self.assertEqual('{"message": "deregistration email has been sent"}', self.getResponseText(resp))

    @test
    def you_need_csrf_token_to_deregister(self):
        resp = self._doDeregistration(False)
        self.assertEquals(resp.status_code, 400)
        self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}', self.getResponseText(resp))

    @test
    def you_need_valid_csrf_token_to_deregister(self):
        resp = self._doDeregistration('invalid')
        self.assertEquals(resp.status_code, 400)
        self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}', self.getResponseText(resp))

    @test
    def deregistration_needs_a_logged_in_user(self):
        resp = self._doDeregistration(nologin=True)
        self.assertEquals(resp.status_code, 403)
        self.assertEqual('{"errors": ["not logged in"]}', self.getResponseText(resp))

    def _doDeregisterDoit(self, client, csrf=None, secret=None, nologin=None):
        if nologin is None:
            self.login(client)
        self.data = dict()
        self.addDataBasedOnOptionValue('csrf_token', csrf, self.getCSRF(client))
        self.addDataBasedOnOptionValue('deregister_secret', secret, self.secret)
        resp = client.post(config.BASE_URL + '/v1/deregister_doit', data=self.data)
        return resp

    @test
    def you_need_csrf_token_and_secret_for_deregister_doit(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client)
            self.assertEquals(resp.status_code, 200)
            self.assertEqual('{"message": "you are deregistered"}', self.getResponseText(resp))

    @test
    def you_need_secret_for_deregister_doit(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client,secret=False)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["deregister_secret: Field must be at least 8 characters long.", "deregister_secret: secret should contain lowercase", "deregister_secret: secret should contain digit"]}', self.getResponseText(resp))

    @test
    def you_need_valid_csrf_token_for_deregister_doit(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client, csrf= "invalid")
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}', self.getResponseText(resp))

    @test
    def deregistration_doit_needs_a_logged_in_user(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client, nologin=True)
            self.assertEquals(resp.status_code, 403)
            self.assertEqual('{"errors": ["not logged in"]}', self.getResponseText(resp))

    @test
    def you_need_deregister_secret_for_deregister_doit(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client, secret=False)
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["deregister_secret: Field must be at least 8 characters long.", "deregister_secret: secret should contain lowercase", "deregister_secret: secret should contain digit"]}', self.getResponseText(resp))

    @test
    def you_need_valid_deregister_secret_for_deregister_doit(self):
        self._doDeregistration()
        with app.test_client() as client:
            resp = self._doDeregisterDoit(client, secret=uuid4())
            self.assertEquals(resp.status_code, 400)
            self.assertEqual('{"errors": ["bad deregistration secret"]}', self.getResponseText(resp))
