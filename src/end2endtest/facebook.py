import unittest, time
import config
from twatson.unittest_annotations import Fixture, test
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from end2endtest.BrowserSetup import BrowserSetup
from test.helpers.todeprecate.UserTesting import UserTesting

class EndUserRegistrationAndLoginWithFacebookTest(Fixture, UserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def if_a_user_without_public_email_tries_to_register_to_facebook_we_ask_for_email_address(self):
        if config.skipFacebookTests:
            return
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        self.switchToTab('registration')
        driver.find_element_by_id("Facebook_registration_button").click()
        time.sleep(1)
        self._switchWindow(driver)
        driver.find_element_by_id("pass").clear()
        driver.find_element_by_id("pass").send_keys(config.fbpassword)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        time.sleep(5)
        body = driver.find_element_by_id("PopupWindow_MessageDiv").text
        self.assertEqual("please give us an email in the registration form", body)

    @test
    def it_is_possible_to_register_with_facebook(self):
        if config.skipFacebookTests:
            return
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        self.switchToTab('registration')
        driver.find_element_by_id("Facebook_registration_button").click()
        time.sleep(1)
        self._switchWindow(driver)
        driver.find_element_by_id("pass").clear()
        driver.find_element_by_id("pass").send_keys(config.fbpassword2)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser2)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        time.sleep(5)
        body = driver.find_element_by_id("PopupWindow_SuccessDiv").text
        self.assertTrue("mag+elekne@magwas.rulez.org"in body)
        self.closePopup()
        self.switchToTab("account")
        body = driver.find_element_by_id("me_Msg").text
        self.assertTrue("mag+elekne@magwas.rulez.org"in body)
        self.user = User.getByEmail(config.fbuser2)
        Credential.getByUser(self.user, "facebook").rm()
        self.user.rm()

    @test
    def you_can_login_using_facebook(self):
        if config.skipFacebookTests:
            return
        self.user = self.createUserWithCredentials("facebook", config.fbuserid, None, config.fbuser)
        self.user.activate()
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        self.switchToTab("login")
        driver.find_element_by_id("Facebook_login_button").click()
        time.sleep(1)
        self._switchWindow(driver)
        driver.find_element_by_id("pass").clear()
        driver.find_element_by_id("pass").send_keys(config.fbpassword)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        time.sleep(1)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("PopupWindow_MessageDiv").text
        self.assertEqual("", body)
        self.closePopup()
        self.switchToTab("account")
        body = driver.find_element_by_id("me_Msg").text
        self.assertTrue("mag+tesztelek@magwas.rulez.org"in body)
        Credential.getByUser(self.user, "facebook").rm()
        self.user.rm()

    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
