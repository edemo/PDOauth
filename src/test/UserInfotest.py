# -*- coding: UTF-8 -*-
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance
import time
from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.ReportedError import ReportedError
from test.helpers.UserUtil import UserUtil
from test.helpers.CryptoTestUtil import CryptoTestUtil
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.AppAssurance import AppAssurance
from pdoauth.models.AppMap import AppMap
from test import config

class UserInfoTest(PDUnitTest, UserUtil, CryptoTestUtil, AuthProviderUtil):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.app = self.createApp()
        self.authProvider = AuthProvider(self.controller.interface)
        self.setDefaultParams()
        self.createLoggedInUser()

    @test
    def logged_in_user_can_get_its_info(self):
        resp = self.showUserByCurrentUser('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('userid'))

    @test
    def userid_returned_is_the_string_one(self):
        resp = self.showUserByCurrentUser('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        userid = data['userid']
        self.assertTrue(isinstance(userid,basestring))
        self.assertTrue('-' in userid)

    @test
    def user_info_contains_assurance(self):
        current_user = self.controller.getCurrentUser()
        myEmail = current_user.email
        now = round(time.time())
        Assurance.new(current_user, 'test', current_user, now)
        Assurance.new(current_user, 'test2', current_user, now)
        Assurance.new(current_user, 'test2', current_user, now)
        resp = self.showUserByCurrentUser('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('assurances'))
        assurances = data['assurances']
        assurance = assurances['test'][0]
        self.assertEqual(assurance['assurer'], myEmail)
        self.assertEqual(assurance['user'], myEmail)
        self.assertEqual(round(assurance['timestamp']), now)
        self.assertEqual(assurance['readable_time'], time.asctime(time.gmtime(now)))
        self.assertEqual(len(assurances['test2']),2)

    @test
    def user_info_contains_hash(self):
        current_user = self.controller.getCurrentUser()
        current_user.hash = self.createHash()
        current_user.save()
        resp = self.showUserByCurrentUser('me')
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertEquals(data['hash'],current_user.hash)

    def _createAssurer(self):
        current_user = self.controller.getCurrentUser()
        Assurance.new(current_user, 'assurer', current_user)
        return current_user

    @test
    def users_with_assurer_assurance_can_get_email_and_digest_for_anyone(self):
        current_user = self._createAssurer()
        targetuser=self.createUserWithCredentials().user
        Assurance.new(targetuser,'test',current_user)
        target = User.getByEmail(self.userCreationEmail)
        resp = self.showUserByCurrentUser(target.userid)
        data = self.fromJson(resp)
        assurances = data['assurances']
        self.assertEquals(assurances['test'][0]['assurer'], current_user.email)

    @test
    def users_without_assurer_assurance_cannot_get_email_and_digest_for_anyone(self):
        current_user = self.controller.getCurrentUser()
        targetuser=self.createUserWithCredentials().user
        Assurance.new(targetuser,'test',current_user)
        target = User.getByEmail(self.userCreationEmail)
        with self.assertRaises(ReportedError) as context:
            self.showUserByCurrentUser(target.userid)
        self.assertTrue(context.exception.status,403)

    @test
    def users_with_assurer_assurance_can_get_user_by_email(self):
        self._createAssurer()
        self.setupRandom()
        self.createUserWithCredentials()
        target = User.getByEmail(self.userCreationEmail)
        resp = self.controller.doGetByEmail(target.email)
        self.assertUserResponse(resp)

    @test
    def no_by_email_with_wrong_email(self):
        self._createAssurer()
        self.setupRandom()
        self.createUserWithCredentials()
        target = User.getByEmail(self.userCreationEmail)
        with self.assertRaises(ReportedError) as context:
            self.controller.doGetByEmail('u'+target.email)
        self.assertTrue(context.exception.status,404)

    @test
    def users_without_assurer_assurance_cannot_get_user_by_email(self):
        user = self.createUserWithCredentials()
        self.assertTrue(user is not None)
        target = User.getByEmail(self.userCreationEmail)
        with self.assertRaises(ReportedError) as context:
            self.controller.doGetByEmail(target.email)
        self.assertTrue(context.exception.status,403)

    @test
    def user_id_shown_to_the_application_differs_from_the_user_id(self):
        userid = self.cred.user.userid
        userinfo = self.getUserInfo()
        self.assertTrue(userid != userinfo['userid'])

    @test
    def user_id_shown_to_the_application_does_not_change_over_time(self):
        tokens = self.obtainCodeAndCallTokenInterface()
        userinfo1 = self.showUserByServer(tokens)
        Assurance.new(self.cred.user, 'test', self.cred.user)
        userinfo2 = self.showUserByServer(tokens)
        self.assertEqual(userinfo1['userid'], userinfo2['userid'])

    @test
    def email_shown_to_the_application_does_not_change_over_time(self):
        tokens = self.obtainCodeAndCallTokenInterface()
        userinfo1 = self.showUserByServer(tokens)
        Assurance.new(self.cred.user, 'test', self.cred.user)
        userinfo2 = self.showUserByServer(tokens)
        self.assertEqual(userinfo1['email'], userinfo2['email'])

    @test
    def the_userid_shown_for_the_same_user_should_be_different_for_different_applications(self):
        userinfo1 = self.getUserInfo()
        self.prepareGetUserInfo()
        userinfo2 = self.getUserInfo()
        self.assertTrue(userinfo1['userid'] != userinfo2['userid'])

    @test
    def the_email_address_shown_for_the_same_user_should_be_different_for_different_applications(self):
        userinfo1 = self.getUserInfo()
        self.prepareGetUserInfo()
        userinfo2 = self.getUserInfo()
        self.assertTrue(userinfo1['email'] != userinfo2['email'])

    @test
    def the_email_address_shown_for_the_user_is_userid_dot_appname_at_EMAILDOMAIN(self):
        userinfo1 = self.getUserInfo()
        appMapEntry = AppMap.get(self.app, self.cred.user)
        emailAddress = "{0}.{1}@{2}".format(
                        appMapEntry.userid,
                        self.app.name,
                        config.Config.EMAIL_DOMAIN)
        self.assertEqual(userinfo1['email'], emailAddress)
        self.assertEqual(userinfo1['email'], appMapEntry.getEmail())

    @test
    def the_applications_do_not_receive_credential_data_from_the_user(self):
        userinfo = self.getUserInfo()
        self.assertTrue(not userinfo.has_key('credentials'))

    @test
    def the_applications_do_not_receive_hash_from_the_user(self):
        userinfo = self.getUserInfo()
        self.assertTrue(not userinfo.has_key('hash'))

    @test
    def for_each_application_there_is_a_list_of_assurances_used_by_that_applications(self):
        AppAssurance.get(self.app)

    @test
    def assurance_list_for_applications_contain_the_assurances_added(self):
        AppAssurance.add(self.app, 'test')
        assuranceList = AppAssurance.get(self.app)
        self.assertEqual(assuranceList, ['test'])

    @test
    def if_you_add_the_same_assurance_the_second_time__it_will_have_no_effect(self):
        AppAssurance.add(self.app, 'test')
        AppAssurance.add(self.app, 'test')
        assuranceList = AppAssurance.get(self.app)
        self.assertEqual(assuranceList, ['test'])

    @test
    def the_applications_receive_intersection_of_users_assurances_and_applications_assurances(self):
        AppAssurance.add(self.app, 'test')
        AppAssurance.add(self.app, 'test2')
        user = self.cred.user
        Assurance.new(user, "test", user)
        Assurance.new(user, "test3", user)
        userinfo = self.getUserInfo()
        self.assertEqual(userinfo['assurances'], ['test'])

    @test
    def the_applications_do_not_receive_anything_beyond_mapped_email_address__mapped_user_id_and_filtered_list_of_assurance_names(self):
        userinfo = self.getUserInfo()
        self.assertEquals(userinfo.keys(),['userid', 'assurances', 'email'])
