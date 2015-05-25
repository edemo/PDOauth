from selenium import webdriver
import unittest
import config
from twatson.unittest_annotations import Fixture, test
import os
from test.TestUtil import UserTesting
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

class SSLAuthTest(Fixture, UserTesting):
    def setUp(self):
        self.profile_diretory = os.path.join(os.path.dirname(__file__), "firefox-client-ssl-profile")
        self.assertTrue(os.path.exists(self.profile_diretory))

        self.profile2 = FirefoxProfile(self.profile_diretory)
        self.profile2.set_preference("security.default_personal_cert", "Select Automatically")
        self.defcertDriver = webdriver.Firefox(firefox_profile=self.profile2)
        self.defcertDriver.implicitly_wait(10)
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def ssl_login_logs_in_if_you_are_registered_and_have_cert(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        user = self.createUserWithCredentials("certificate", identifier, digest, "certuser@example.org")
        driver = self.defcertDriver
        #pdb.set_trace()
        driver.get(config.Config.SSL_LOGIN_URL)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            body)
        self.deleteUser(user)

    @test
    def normal_pages_do_not_ask_for_cert(self):
        profile = FirefoxProfile(self.profile_diretory)
        driver = webdriver.Firefox(firefox_profile=profile)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(10)
        driver.get(self.base_url+"/static/login.html")
        body = driver.find_element_by_id("PasswordResetForm_password_label").text
        self.assertEqual(body, u'New password:')
        driver.quit()

    def tearDown(self):
        self.defcertDriver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
