# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.User import User
import json
from test.TestUtil import UserTesting
from flask_login import current_user
from pdoauth.models.Assurance import Assurance
import time

class UserInfoTest(Fixture, UserTesting):

    @test
    def logged_in_user_can_get_its_info(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('userid'))

    @test
    def userid_returned_is_the_string_one(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            userid = data['userid']
            self.assertTrue(isinstance(userid,basestring))
            self.assertTrue('-' in userid)

    @test
    def user_info_contains_assurance(self):
        with app.test_client() as c:
            self.login(c)
            myEmail = current_user.email
            now = time.time()
            Assurance.new(current_user, 'test', current_user, now)
            Assurance.new(current_user, 'test2', current_user, now)
            Assurance.new(current_user, 'test2', current_user, now)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('assurances'))
            assurances = data['assurances']
            assurance = assurances['test'][0]
            self.assertEqual(assurance['assurer'], myEmail)
            self.assertEqual(assurance['user'], myEmail)
            self.assertEqual(assurance['timestamp'], now)
            self.assertEqual(assurance['readable_time'], time.asctime(time.gmtime(now)))
            self.assertEqual(len(assurances['test2']),2)
    @test
    def users_with_assurer_assurance_can_get_email_and_digest_for_anyone(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            targetuser=self.create_user_with_credentials()
            Assurance.new(targetuser,'test',current_user)
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/users/{0}'.format(target.userid))
            text = self.getResponseText(resp)
            data = json.loads(text)
            assurances = data['assurances']
            self.assertEquals(assurances['test'][0]['assurer'], current_user.email)

    @test
    def users_without_assurer_assurance_cannot_get_email_and_digest_for_anyone(self):
        with app.test_client() as c:
            self.login(c)
            targetuser=self.create_user_with_credentials()
            Assurance.new(targetuser,'test',current_user)
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/users/{0}'.format(target.id))
            self.assertEqual(403, resp.status_code)

    @test
    def users_with_assurer_assurance_can_get_user_by_email(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            self.setupRandom()
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertUserResponse(resp)

    @test
    def no_by_email_with_wrong_email(self):
        with app.test_client() as c:
            self.login(c)
            Assurance.new(current_user, 'assurer', current_user)
            self.setupRandom()
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/u{0}'.format(target.email))
            self.assertEquals(resp.status_code,404)

    @test
    def users_without_assurer_assurance_cannot_get_user_by_email(self):
        with app.test_client() as c:
            self.login(c)
            user = self.create_user_with_credentials()
            self.assertTrue(user is not None)
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertEquals(resp.status_code,403)

    @test
    def users_without_login_cannot_get_user_by_email(self):
        with app.test_client() as c:
            self.create_user_with_credentials()
            target = User.getByEmail(self.usercreation_email)
            resp = c.get('http://localhost.local/v1/user_by_email/{0}'.format(target.email))
            self.assertEquals(resp.status_code,302)
            self.assertEquals(resp.headers['Location'],"http://localhost.local/static/login.html")
