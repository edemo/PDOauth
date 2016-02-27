# -*- coding: UTF-8 -*-
import unittest
from pdoauth.app import app
from pdoauth.models.User import User
import time
from end2endtest.helpers.EndUserTesting import EndUserTesting, test

class SslAuthTest(EndUserTesting):

    def setUp(self):
        EndUserTesting.setUp(self)
        self.setupUserCreationData()

    def _keygenAndLogin(self):
        self.driver.get(app.config.get("START_URL"))

        self.switchToTab('registration')
        emailField = self.driver.find_element_by_id("KeygenForm_email_input")
        emailField.clear()
        emailField.send_keys(self.userCreationEmail)
        self.driver.find_element_by_id("KeygenForm_submit").click()
        time.sleep(4)
        user = User.getByEmail(self.userCreationEmail)
        self.assertTrue(user)
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        self.driver.get(sslLoginBaseUrl + '/v1/ssl_login')
        self.driver.get(sslLoginBaseUrl + '/v1/users/me')
        time.sleep(1)
        body = self.driver.find_element_by_css_selector("BODY").text
        credentialText = '{"credentialType": "certificate", "identifier": '
        self.assertTrue(credentialText in body)
        self.assertTrue('/{0}"}}'.format(self.userCreationEmail) in
            body)

    def _logoutAfterKeygen(self):
        self.driver.get(app.config.get("START_URL"))
        self.switchToTab("account")
        self.driver.find_element_by_id("logout_button").click()
        time.sleep(1)
        body = self.driver.find_element_by_id("PopupWindow_MessageDiv").text
        self.assertEqual(body, "message\nlogged out")
        self.closePopup()

    @test
    def ssl_login_logs_in_if_you_are_registered_and_have_cert(self):
        self._keygenAndLogin()
        time.sleep(1)
        self._logoutAfterKeygen()
        time.sleep(1)
        self.driver.get(app.config.get("START_URL"))
        self.switchToTab("login")
        self.driver.find_element_by_id("ssl_login").click()
        time.sleep(1)
        self.switchToTab("account")
        self.driver.find_element_by_id("melink").click()
        time.sleep(1)
        self.assertEqual(self.driver.find_element_by_id("PopupWindow_ErrorDiv").text, "")
        userData = self.driver.find_element_by_id("me_Msg").text
        self.assertTrue("{0}".format(self.userCreationEmail) in
                userData)
        self.deleteCerts()

    @test
    def ssl_login_registers_and_logs_in_if_you_have_cert_and_give_email(self):
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        user = User.getByEmail(self.userCreationEmail)
        self.deleteUser(user)
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        self.driver.get(sslLoginBaseUrl + '/v1/ssl_login?email=hello@example.com')
        time.sleep(1)
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
        self.driver.get(baseUrl + '/v1/ssl_login')
        self.driver.get(baseUrl + '/v1/users/me')
        user = User.getByEmail(self.userCreationEmail)
        self.deleteUser(user)
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertEqual('{"errors": ["no authorization"]}', body)
        self.deleteCerts()

    @test
    def the_SSl_LOGIN_BASE_URL_page_works_if_no_cert_is_given(self):
        self.deleteCerts()
        startUrl = app.config.get("START_URL")
        baseUrl = app.config.get("BASE_URL")
        sslLoginBaseUrl = app.config.get("SSL_LOGIN_BASE_URL")
        testUrl = startUrl.replace(baseUrl, sslLoginBaseUrl)
        self.driver.get(testUrl)
        time.sleep(1)
        body = self.driver.find_element_by_css_selector("BODY").text
        self.assertTrue(u'Bejelentkezési lehetőségek' in body)

    @test
    def normal_pages_do_not_ask_for_cert(self):
        self._keygenAndLogin()
        self._logoutAfterKeygen()
        startUrl = app.config.get("START_URL")
        self.driver.get(startUrl)
        self.switchToTab("login")
        passwordId = "PasswordResetForm_OnLoginTab_password_label"
        body = self.driver.find_element_by_id(passwordId).text
        self.assertEqual(body, u'Új jelszó:')
        self.deleteCerts()

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
