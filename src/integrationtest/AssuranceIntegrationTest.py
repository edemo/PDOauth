# -*- coding: UTF-8 -*-
from pdoauth.app import app
from pdoauth.models.Assurance import Assurance
from uuid import uuid4
from flask_login import current_user
from integrationtest import config
from integrationtest.helpers.CSRFMixin import CSRFMixin
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest

class AssuranceIntegrationTest(IntegrationTest, CSRFMixin, UserTesting):

    def _createUserWithHash(self):
        target = self.createUserWithCredentials().user
        target.hash = self.createHash()
        target.activate()
        target.save()
        return target

    def _setupTestWithoutAssurance(self, client):
        self.login(client)
        target = self._createUserWithHash()
        self.assertTrue('test' not in Assurance.getByUser(target))
        return target

    def _setupTest(self, client):
        target = self._setupTestWithoutAssurance(client)
        Assurance.new(current_user, 'assurer', current_user)
        Assurance.new(current_user, 'assurer.test', current_user)
        return target


    
    def test_assurance_form_needs_csrf(self):
        with app.test_client() as client:
            self.login(client)
            data = dict(
                digest = self.createHash(),
                assurance = "test",
                email = "invalid@email.com",
                csrf_token = "")
            resp = client.post(config.BASE_URL + '/v1/add_assurance', data = data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual(self.getResponseText(resp),'{"errors": ["csrf_token: csrf validation error"]}')

    
    def test_assurers_with_appropriate_credential_can_add_assurance_to_user_using_hash(self):
        """
        the appropriate credential is an assurance in the form "assurer.<assurance_name>"
        where assurance_name is the assurance to be added
        """
        with app.test_client() as client:
            target = self._setupTest(client)
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(client))
            resp = client.post(config.BASE_URL + '/v1/add_assurance', data = data)
            self.assertEqual(200, resp.status_code)
            self.assertEqual(Assurance.getByUser(target)['test'][0]['assurer'], current_user.email)

    
    def test_no_madeup_csrf_cookie(self):
        with app.test_client() as client:
            target = self._setupTest(client)
            false_cookie=uuid4().hex
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = false_cookie)
            client.set_cookie("localhost.localdomain","csrf",false_cookie)
            resp = client.post(config.BASE_URL + '/v1/add_assurance', data = data)
            self.assertEqual(400, resp.status_code)
            self.assertEqual('{"errors": ["csrf_token: csrf validation error"]}',self.getResponseText(resp))
