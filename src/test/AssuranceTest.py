# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.User import User
from test.TestUtil import UserTesting, CSRFMixin
from pdoauth.models.Assurance import Assurance
from uuid import uuid4
from flask_login import current_user
import config

class AssuranceTest(Fixture, CSRFMixin, UserTesting):

    def _setupTestWithoutAssurance(self, c):
        self.login(c)
        self.createUserWithCredentials()
        target = User.getByEmail(self.usercreation_email)
        target.hash = self.createHash()
        target.save()
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

    @test
    def assurers_without_appropriate_credential_cannot_add_assurance_to_user(self):
        with app.test_client() as c:
            target = self._setupTestWithoutAssurance(c)
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(403, resp.status_code)

    @test
    def adding_assurance_is_possible_using_the_hash_only(self):
        with app.test_client() as c:
            target = self._setupTest(c)
            data = dict(
                digest = target.hash,
                assurance = "test",
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(200, resp.status_code)
            self.assertEquals(Assurance.getByUser(target)['test'][0]['assurer'], current_user.email)

    @test
    def assurers_need_assurer_assurance(self):
        with app.test_client() as c:
            target = self._setupTestWithoutAssurance(c)
            Assurance.new(current_user, 'assurer.test', current_user)
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(403, resp.status_code)
            self.assertEquals('{"errors": ["no authorization"]}', self.getResponseText(resp))

    @test
    def assurers_need_giving_assurance(self):
        "that is they have to have assurance.[the assurance to give]"
        with app.test_client() as c:
            target = self._setupTestWithoutAssurance(c)
            Assurance.new(current_user, 'assurer', current_user)
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(403, resp.status_code)
            self.assertEquals('{"errors": ["no authorization"]}', self.getResponseText(resp))

    @test
    def when_an_assurer_wants_to_add_an_assurance_for_a_user_with_hash_and_without_email___and_there_are_multiple_users_with_that_hash___then_an_error_is_signaled(self):
        with app.test_client() as c:
            target = self._setupTest(c)
            anotherUser = self.createUserWithCredentials()
            anotherUser.hash = target.hash
            anotherUser.save()
            data = dict(
                digest = target.hash,
                assurance = "test",
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(400, resp.status_code)
            self.assertEquals('{"errors": ["Two users with the same hash; specify both hash and email"]}', self.getResponseText(resp))

    @test
    def when_an_assurance_added_with_hash_and_email___and_there_is_another_user_with_the_same_hash___the_hash_from_the_other_user_is_deleted(self):
        with app.test_client() as c:
            target = self._setupTest(c)
            anotherUser = self.createUserWithCredentials()
            anotherEmail = self.usercreation_email
            anotherUser.hash = target.hash
            targetHash = target.hash
            anotherUser.save()
            data = dict(
                digest = target.hash,
                assurance = "test",
                email = target.email,
                csrf_token = self.getCSRF(c))
            resp = c.post(config.base_url + '/v1/add_assurance', data = data)
            self.assertEquals(200, resp.status_code)
            self.assertEquals(Assurance.getByUser(target)['test'][0]['assurer'], current_user.email)
            anotherUser = User.getByEmail(anotherEmail)
            self.assertEqual(anotherUser.hash, None)
            user = User.getByEmail(target.email)
            self.assertEqual(user.hash, targetHash)

    @test
    def adding_assurance_with_invalid_hash_and_no_email_fails(self):
        self.fail()
    
    @test
    def adding_assurance_with_invalid_hash_and_email_fails(self):
        self.fail()

    @test
    def adding_assurance_with_email_and_hash_of_someone_other_fails(self):
        self.fail()
