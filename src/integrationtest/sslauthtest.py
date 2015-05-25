from selenium import webdriver
import unittest
import config
from twatson.unittest_annotations import Fixture, test
import os
from test.TestUtil import UserTesting
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import pdb
from OpenSSL import crypto
from pdoauth.models.Credential import Credential

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

    def _getCertAttributes(self):
        certFileName = os.path.join(os.path.dirname(__file__), "client.crt")
        certFile = open(certFileName)
        cert = certFile.read()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName
        identifier = "{0}/{1}".format(digest, 
            cn)
        return identifier, digest

    @test
    def ssl_login_logs_in_if_you_are_registered_and_have_cert(self):
        identifier, digest = self._getCertAttributes()
        user = self.createUserWithCredentials("certificate", identifier, digest, "certuser@example.org")
        driver = self.defcertDriver
        #pdb.set_trace()
        driver.get(config.Config.SSL_LOGIN_URL)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertEqual(body, u'{"message": "You are logged in"}')
        for cred in Credential.getByUser(user):
            cred.rm()
        user.rm()


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
