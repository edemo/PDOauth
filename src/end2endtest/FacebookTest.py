# coding: UTF-8
from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil
import config

class FacebookTest(Fixture, BrowsingUtil):

    @test
    def it_is_possible_to_register_with_facebook(self):
        self.goToLoginPage()
        fbUser = config.facebookUser2
        self.handleFbRegistration(user=fbUser)
        self.assertTextInPopupTitle(u'GRATULÁLUNK!')
        
    @test
    def if_a_user_without_public_email_tries_to_register_to_facebook_we_ask_for_email_address(self):
        self.goToLoginPage()
        self.handleFbRegistration(user=config.facebookUser1)
        self.assertPopupErrorMatchesRe(r"Nem j. az email-c.m")

    @test
    def you_can_login_using_facebook(self):
        self.goToLoginPage()
        self.handleFbRegistration()
        self.logOut()
        self.logoutFromFacebook()
        self.goToLoginPage()
        self.handleFbLogin()
        self.assertFbUserIsLoggedIn()

    def tearDown(self):
        self.removeFbuser(user=config.facebookUser1)
        self.logoutFromFacebook()
        BrowsingUtil.tearDown(self)