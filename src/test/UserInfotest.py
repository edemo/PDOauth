# -*- coding: UTF-8 -*-
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance
import time
from test.helpers.todeprecate.UserTesting import UserTesting
from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.ReportedError import ReportedError

class UserInfoTest(PDUnitTest, UserTesting):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.current_user = self.createLoggedInUser()

    @test
    def logged_in_user_can_get_its_info(self):
        resp = self.controller._do_show_user(userid='me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('userid'))

    @test
    def userid_returned_is_the_string_one(self):
        resp = self.controller._do_show_user('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        userid = data['userid']
        self.assertTrue(isinstance(userid,basestring))
        self.assertTrue('-' in userid)

    @test
    def user_info_contains_assurance(self):
        current_user = self.current_user
        myEmail = current_user.email
        now = time.time()
        Assurance.new(current_user, 'test', current_user, now)
        Assurance.new(current_user, 'test2', current_user, now)
        Assurance.new(current_user, 'test2', current_user, now)
        resp = self.controller._do_show_user('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('assurances'))
        assurances = data['assurances']
        assurance = assurances['test'][0]
        self.assertEqual(assurance['assurer'], myEmail)
        self.assertEqual(assurance['user'], myEmail)
        self.assertEqual(assurance['timestamp'], now)
        self.assertEqual(assurance['readable_time'], time.asctime(time.gmtime(now)))
        self.assertEqual(len(assurances['test2']),2)

    @test
    def user_info_contains_hash(self):
        current_user = self.current_user
        current_user.hash = self.createHash()
        current_user.save()
        resp = self.controller._do_show_user('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertEquals(data['hash'],current_user.hash)
        self.tearDownController()

    @test
    def users_with_assurer_assurance_can_get_email_and_digest_for_anyone(self):
        current_user = self.current_user
        Assurance.new(current_user, 'assurer', current_user)
        targetuser=self.createUserWithCredentials()
        Assurance.new(targetuser,'test',current_user)
        target = User.getByEmail(self.usercreation_email)
        resp = self.controller._do_show_user(target.userid)
        data = self.fromJson(resp)
        assurances = data['assurances']
        self.assertEquals(assurances['test'][0]['assurer'], current_user.email)
 
    @test
    def users_without_assurer_assurance_cannot_get_email_and_digest_for_anyone(self):
        current_user = self.current_user
        targetuser=self.createUserWithCredentials()
        Assurance.new(targetuser,'test',current_user)
        target = User.getByEmail(self.usercreation_email)
        with self.assertRaises(ReportedError) as e:
            self.controller._do_show_user(target.id)
        self.assertTrue(e.exception.status,403)

    @test
    def users_with_assurer_assurance_can_get_user_by_email(self):
        current_user = self.current_user
        Assurance.new(current_user, 'assurer', current_user)
        self.setupRandom()
        self.createUserWithCredentials()
        target = User.getByEmail(self.usercreation_email)
        resp = self.controller.do_get_by_email(target.email)
        self.assertUserResponse(resp)

    @test
    def no_by_email_with_wrong_email(self):
        current_user = self.current_user
        Assurance.new(current_user, 'assurer', current_user)
        self.setupRandom()
        self.createUserWithCredentials()
        target = User.getByEmail(self.usercreation_email)
        with self.assertRaises(ReportedError) as e:
            self.controller._do_get_by_email('u'+target.email)
        self.assertTrue(e.exception.status,404)

    @test
    def users_without_assurer_assurance_cannot_get_user_by_email(self):
        user = self.createUserWithCredentials()
        self.assertTrue(user is not None)
        target = User.getByEmail(self.usercreation_email)
        with self.assertRaises(ReportedError) as e:
            self.controller._do_get_by_email(target.email)
        self.assertTrue(e.exception.status,403)

    @test
    def users_without_login_cannot_get_user_by_email(self):
        self.controller._testdata.current_user = None
        self.createUserWithCredentials()
        target = User.getByEmail(self.usercreation_email)
        with self.assertRaises(ReportedError) as e:
            self.controller._do_get_by_email(target.email)
        self.assertEquals(e.exception.status,403)
