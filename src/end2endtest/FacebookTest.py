from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil
from selenium.webdriver.common.by import By
import config

class FacebookTest(Fixture, BrowsingUtil):
    @test
    def if_a_user_without_public_email_tries_to_register_to_facebook_we_ask_for_email_address(self):
        self.goToLoginPage()
        self.handleFbRegistration(user=config.facebookUser1)
        self.wait_on_element_text(By.ID, "PopupWindow_CloseButton", "Close")
        self.assertPopupTextIs("please give us an email in the registration form")

    @test
    def it_is_possible_to_register_with_facebook(self):
        if config.skipFacebookTests:
            return
        self.goToLoginPage()
        fbUser = config.facebookUser2
        self.handleFbRegistration(user=fbUser)
        self.assertFbUserIsLoggedIn(user=fbUser)
        
    @test
    def you_can_login_using_facebook(self):
        if config.skipFacebookTests:
            return
        self.goToLoginPage()
        self.handleFbRegistration()
        self.logOut()
        self.handleFbLogin()
        self.assertFbUserIsLoggedIn()

    def tearDown(self):
        self.removeFbuser(user=config.facebookUser1)
        self.logoutFromFacebook()
        BrowsingUtil.tearDown(self)