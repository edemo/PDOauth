# -*- coding: UTF-8 -*-
import unittest
import config
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.User import User
from end2endtest.BrowserSetup import BrowserSetup
import time
from test.helpers.todeprecate.UserTesting import UserTesting

class SSLAuthTest(Fixture, UserTesting, BrowserSetup):

    def setUp(self):
        self.setupDriver()
        self.setupUserCreationData()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    def _keygenAndLogin(self):
        self.driver.get(app.config.get("START_URL"))
        self.driver.execute_script("document.getElementById('tab-content-registration').style.visibility = 'visible'")
        self.driver.find_element_by_id("KeygenForm_email_input").clear()
        self.driver.find_element_by_id("KeygenForm_email_input").send_keys(self.usercreation_email)
        self.driver.find_element_by_id("KeygenForm_createuser_input").click()
        self.driver.find_element_by_id("KeygenForm_submit").click()
        time.sleep(1)
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        self.driver.get(sslLoginBaseUrl + '/ssl_login')
        self.driver.get(sslLoginBaseUrl + '/v1/users/me')
        time.sleep(1)
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertTrue('{"credentialType": "certificate", "identifier": ' in body)
        self.assertTrue('/{0}"}}'.format(self.usercreation_email) in
            body)


    def _logoutAfterKeygen(self):
        self.driver.get(app.config.get("START_URL"))
        self.switchToTab("account")
        self.driver.find_element_by_id("logout_button").click()
        time.sleep(1)
        self.driver.get(app.config.get("START_URL"))
        self.switchToTab("account")
        self.driver.find_element_by_id("melink").click()
        body = self.driver.find_element_by_id("errorMsg").text
        self.assertEqual(body, "no authorization")

    @test
    def ssl_login_logs_in_if_you_are_registered_and_have_cert(self):
        identifier, digest, cert = self.getCertAttributes()  # @UnusedVariable
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        self.driver.get(app.config.get("START_URL"))
        self.switchToTab("login")
        self.driver.find_element_by_id("ssl_login").click()
        self.switchToTab("account")
        self.driver.find_element_by_id("melink").click()
        self.assertEqual(self.driver.find_element_by_id("errorMsg").text, "")
        userData = self.driver.find_element_by_id("userdata").text
        self.assertTrue("email: {0}\nuserid: ".format(self.usercreation_email) in
                userData)
        self.deleteCerts()
        

    @test
    def ssl_login_registers_and_logs_in_if_you_have_cert_and_give_email(self):
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        user = User.getByEmail(self.usercreation_email)
        self.deleteUser(user)
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        self.driver.get(sslLoginBaseUrl + '/ssl_login?email=hello@example.com')
        self.driver.get(sslLoginBaseUrl + '/v1/users/me')
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertTrue('{"credentialType": "certificate", "identifier": "' in
            body)
        self.assertTrue('"email": "hello@example.com"' in body)
        user = User.getByEmail("hello@example.com")
        self.deleteUser(user)
        self.deleteCerts()
 
    @test
    def no_ssl_login_on_base_url(self):
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        baseUrl = app.config.get("BASE_URL")
        self.driver.get(baseUrl + '/ssl_login')
        self.driver.get(baseUrl + '/v1/users/me')
        user = User.getByEmail(self.usercreation_email)
        self.deleteUser(user)
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertEqual('{"errors": ["no authorization"]}', body)
        self.deleteCerts()

    @test
    def SSl_LOGIN_BASE_URL_works_if_no_cert_is_given(self):
        startUrl = app.config.get("START_URL")
        baseUrl = app.config.get("BASE_URL")
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        testUrl = startUrl.replace(baseUrl, sslLoginBaseUrl)
        self.driver.get(testUrl)
        self.switchToTab("account")
        body = self.driver.find_element_by_id("PasswordResetForm_password_label").text
        self.assertEqual(body, u'Új jelszó:')
        self.driver.get(sslLoginBaseUrl + '/ssl_login')
        time.sleep(1)
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertEqual('{"errors": ["No certificate given"]}', body)

    @test
    def normal_pages_do_not_ask_for_cert(self):
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        startUrl = app.config.get("START_URL")
        self.driver.get(startUrl)
        self.switchToTab("account")
        body = self.driver.find_element_by_id("PasswordResetForm_password_label").text
        self.assertEqual(body, u'Új jelszó:')
        self.deleteCerts()

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
