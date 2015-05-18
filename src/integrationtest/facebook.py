from selenium import webdriver
import unittest, time
import config
from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.models.Credential import Credential

class EndUserRegistrationAndLoginWithFacebook(Fixture, UserTesting):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "http://"+ config.Config.SERVER_NAME
        self.verificationErrors = []

    @test
    def if_a_user_without_public_email_tries_to_register_to_facebook_we_ask_for_email_address(self):
        if config.skipFacebookTests:
            return
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
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
        driver.find_element_by_id("pass").send_keys(config.fbpassword)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        time.sleep(5)
        body = driver.find_element_by_id("message").text
        self.assertEqual("please give us an email in the registration form", body)


    @test
    def you_can_login_using_facebook(self):
        if config.skipFacebookTests:
            return
        self.user = self.createUserWithCredentials("facebook", config.fbuserid, None, config.fbuser)
        self.user.activate()
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        driver.find_element_by_id("Facebook_login_button").click()
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
        driver.find_element_by_id("pass").send_keys(config.fbpassword)
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(config.fbuser)
        driver.find_element_by_id("u_0_2").click()
        driver.switch_to.window(self.master)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("message").text
        self.assertEqual("", body)
        body = driver.find_element_by_id("userdata").text
        self.assertTrue("email: mag+tesztelek@magwas.rulez.org"in body)
        Credential.getByUser(self.user, "facebook").rm()
        self.user.rm()

    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
