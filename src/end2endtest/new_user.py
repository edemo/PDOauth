import unittest
import config
from twatson.unittest_annotations import Fixture, test
from pdoauth.models.Application import Application
import time
from urllib import urlencode
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from end2endtest.BrowserSetup import BrowserSetup
from test.helpers.todeprecate.UserTesting import UserTesting

class NewUserTest(Fixture,UserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []
        self._setupApp()

    def _setupApp(self):
        self.setupRandom()
        self.redirect_uri = "https://app-{0}.github.com/".format(self.randString)
        self.appname = "testapp{0}".format(self.randString)
        self.app = Application.new(self.appname, "S3cret", self.redirect_uri)
        self.assertTrue(self.app)


    def _gotoOauthPage(self, driver):
        fullUri = "{0}/v1/oauth2/auth?{1}".format(self.base_url, 
            urlencode({
                    "response_type":"code", 
                    "client_id":self.app.appid, 
                    "redirect_uri":self.redirect_uri}))
        driver.get(fullUri)
        time.sleep(1)
        uri = "{0}/static/login.html?{1}".format(self.base_url,urlencode({"next": fullUri}))
        self.assertEqual(uri, driver.current_url)
        return fullUri

    @test
    def unregistered_user_can_register_with_password_in_the_middle_of_login_procedure_of_a_served_application(self):
        driver = self.driver
        self._gotoOauthPage(driver)
        userid = "user_{0}".format(self.randString)
        email = "user_{0}@example.com".format(self.randString)
        self.thePassword = self.mkRandomPassword()
        self.switchToTab('registration')
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(userid)
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys(self.mkRandomPassword())
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(2)
        self.assertTrue(driver.current_url.startswith(self.redirect_uri.lower()))

    @test
    def unregistered_user_can_register_with_facebook_in_the_middle_of_login_procedure_of_a_served_application(self):
        if config.skipFacebookTests:
            return
        driver = self.driver
        self._gotoOauthPage(driver)
        self.switchToTab('registration')
        driver.find_element_by_id("Facebook_registration_button").click()
        time.sleep(1)
        self.master = driver.current_window_handle
        timeCount = 1;
        while (len(driver.window_handles) == 1 ):
            time
            timeCount += 1
            if ( timeCount > 50 ): 
                break;
        for handle in driver.window_handles:
            if handle!=self.master:
                driver.switch_to.window(handle)
        driver.find_element_by_id("pass").clear()
        driver.find_element_by_id("pass").send_keys(config.fbpassword2)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser2)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        time.sleep(5)
        self.assertTrue(driver.current_url.startswith(self.redirect_uri.lower()))
        self.user = User.getByEmail(config.fbuser2)
        Credential.getByUser(self.user, "facebook").rm()
        self.user.rm()

    def tearDown(self):
        self.app.rm()
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
