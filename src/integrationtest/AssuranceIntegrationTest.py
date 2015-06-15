# -*- coding: UTF-8 -*-
from pdoauth.app import app
from pdoauth.models.Assurance import Assurance
from uuid import uuid4
from flask_login import current_user
import config
from integrationtest.helpers.CSRFMixin import CSRFMixin
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class AssuranceIntegrationTest(IntegrationTest, CSRFMixin, UserTesting):

    def _createUserWithHash(self):
        target = self.createUserWithCredentials().user
        target.hash = self.createHash()
        target.activate()
        target.save()
        return target

    def _setupTestWithoutAssurance(self, c):
        self.login(c)
        target = self._createUserWithHash()
        self.assertTrue(Assurance.getByUser(target).has_key('test') is False)
        return target

    def _setupTest(self, c):
        target = self._setupTestWithoutAssurance(c)
        Assurance.new(current_user, 'assurer', current_user)
        Assurance.new(current_user, 'assurer.test', current_user)
        return target


    @test
    def assurance_form_needs_csrf(self):
        with app.test_client() as c:
            self.login(c)
            data = dict(
                digest = self.createHash(),
                assurance = "test",
                email = "invalid@email.com",
                csrf_token = "")
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(400, resp.status_code)
            self.assertEquals(self.getResponseText(resp),'{"errors": ["csrf_token: csrf validation error"]}')

    @test
    def assurers_with_appropriate_credential_can_add_assurance_to_user_using_hash(self):
        """
        the appropriate credential is an assurance in the form "assurer.<assurance_name>"
        where assurance_name is the assurance to be added
        """
        with app.test_client() as c:
            target = self._setupTest(c)
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(200, resp.status_code)
            self.assertEquals(Assurance.getByUser(target)['test'][0]['assurer'], current_user.email)

    @test
    def no_madeup_csrf_cookie(self):
        with app.test_client() as c:
            target = self._setupTest(c)
            false_cookie=unicode(uuid4())
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = false_cookie)
            c.set_cookie("localhost.localdomain","csrf",false_cookie)
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(400, resp.status_code)
            self.assertEquals('{"errors": ["csrf_token: csrf validation error"]}',self.getResponseText(resp))
