import unittest
import config
from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.app import app
from selenium.common.exceptions import NoSuchElementException
from pdoauth.models.User import User
from integrationtest.BrowserSetup import BrowserSetup

class SSLAuthTest(Fixture, UserTesting, BrowserSetup):

    def setUp(self):
        self.setupDefCertDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def ssl_login_logs_in_if_you_are_registered_and_have_cert(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        user = self.createUserWithCredentials("certificate", identifier, digest, "certuser@example.org")
        driver = self.defcertDriver
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        driver.get(sslLoginBaseUrl + '/ssl_login')
        driver.get(sslLoginBaseUrl + '/v1/users/me')
        self.deleteUser(user)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            body)

    @test
    def ssl_login_registers_andlogs_in_if_you_are_registered_and_have_cert(self):
        driver = self.defcertDriver
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        driver.get(sslLoginBaseUrl + '/ssl_login?email=hello@example.com')
        body = driver.find_element_by_css_selector("BODY").text
        print body
        driver.get(sslLoginBaseUrl + '/v1/users/me')
        body = driver.find_element_by_css_selector("BODY").text
        print body
        self.assertTrue('{"credentialType": "certificate", "identifier": "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"}' in
            body)
        self.assertTrue('"email": "hello@example.com"' in body)
        user = User.getByEmail("hello@example.com")
        self.deleteUser(user)

    @test
    def no_ssl_login_on_base_url(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        user = self.createUserWithCredentials("certificate", identifier, digest, "certuser@example.org")
        driver = self.defcertDriver
        baseUrl = app.config.get("BASE_URL")
        driver.get(baseUrl + '/ssl_login')
        driver.get(baseUrl + '/v1/users/me')
        self.deleteUser(user)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertEqual('{"errors": ["no authorization"]}', body)

    @test
    def SSL_LOGOUT_URL_does_not_load(self):
        driver = self.defcertDriver
        sslLogoutUrl = app.config.get("SSL_LOGOUT_URL")
        driver.get(sslLogoutUrl)
        self.assertRaises(NoSuchElementException,driver.find_element_by_css_selector,"BODY")

    @test
    def SSl_LOGIN_BASE_URL_works_if_no_cert_is_given(self):
        driver = self.setupDriver()
        startUrl = app.config.get("START_URL")
        baseUrl = app.config.get("BASE_URL")
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        testUrl = startUrl.replace(baseUrl, sslLoginBaseUrl)
        driver.get(testUrl)
        body = driver.find_element_by_id("PasswordResetForm_password_label").text
        self.assertEqual(body, u'New password:')
        driver.get(sslLoginBaseUrl + '/ssl_login')
        body = driver.find_element_by_css_selector("BODY").text
        self.assertEqual('{"errors": ["No certificate given"]}', body)
        driver.quit()

    @test
    def normal_pages_do_not_ask_for_cert(self):
        driver = self.setupCertAskingDriver()
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(10)
        startUrl = app.config.get("START_URL")
        driver.get(startUrl)
        body = driver.find_element_by_id("PasswordResetForm_password_label").text
        self.assertEqual(body, u'New password:')
        driver.quit()


    def tearDown(self):
        self.defcertDriver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
