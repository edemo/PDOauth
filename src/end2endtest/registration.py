#pylint: disable=too-many-instance-attributes
import unittest, time, random, string, json
import assurancetool
import applicationtool
from pdoauth.models.Application import Application
import urllib3
from end2endtest import config
from urllib import urlencode
from end2endtest.helpers.EndUserTesting import EndUserTesting, test

class EndUserRegistrationTest(EndUserTesting):

    def setUp(self):
        EndUserTesting.setUp(self)
        self.setupUserCreationData()
        self.thePassword = self.usercreationPassword
        self.normaluser = self.userCreationUserid
        self.email = self.userCreationEmail
        self.setupUserCreationData()
        self.assurer = self.userCreationUserid
        self.assurerEmail = self.userCreationEmail
        self.assertTrue(self.assurerEmail != self.email)

    def registration_is_done_by_filling_out_the_registration_form(self, driver):
        driver.get(self.baseUrl  + "/static/login.html?next=/v1/users/me")
        driver.refresh()
        self.switchToTab('registration')
        self.theHash = self.createHash()
        self.fillInAndSubmitRegistrationForm(driver, password=self.thePassword, userid=self.normaluser, email=self.email, digest=self.theHash)
        driver.save_screenshot("doc/screenshots/registration.png")
        time.sleep(1)
        self.assertEqual(self.baseUrl  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")

    def if_you_are_not_logged_in__the_authorization_uri_redirects_to_login_page_such_that_after_login_you_can_continue(self, driver):
        uri = self.baseUrl + "/v1/oauth2/auth"
        driver.get(uri)
        driver.refresh()
        time.sleep(1)
        targetUri = "{0}/static/login.html?{1}".format(
            self.baseUrl,
            urlencode({"next": uri}))
        self.assertEqual(targetUri, driver.current_url)


    def _register_assurer(self, driver):
        driver.get(self.baseUrl  + "/static/login.html?next=/v1/users/me")
        driver.refresh()
        self.logout()
        time.sleep(1)
        driver.get(self.baseUrl  + "/static/login.html?next=/v1/users/me")
        driver.refresh()
        self.switchToTab('registration')
        self.fillInAndSubmitRegistrationForm(driver, password=self.thePassword, userid=self.assurer, email=self.assurerEmail)
        time.sleep(3)
        self.assertEqual(self.baseUrl  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")


    def you_can_check_your_data_in_the_ME_url(self, driver):
        driver.get(self.baseUrl  + "/v1/users/me")
        driver.save_screenshot("doc/screenshots/my_data.png")
        time.sleep(1)
        self.assertEqual(self.baseUrl  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")


    def for_some_forms_you_need_a_csrf_token__you_can_obtain_it_by_logging_in(self, driver):
        driver.get(self.baseUrl + "/static/login.html")
        self.logout()
        self.closePopup()
        time.sleep(1)
        self.switchToTab("login")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys(self.assurer)
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys(self.thePassword)
        driver.find_element_by_id("LoginForm_submitButton").click()
        time.sleep(1)
        self.assertEqual(self.baseUrl  + "/static/login.html", driver.current_url)
        time.sleep(1)
        body = driver.find_element_by_id("PopupWindow_SuccessDiv").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.assurerEmail))
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")
        return body


    def an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(self, driver,):
        driver.get(self.baseUrl  + "/static/login.html")
        driver.refresh()
        self.switchToTab("assurer")
        driver.find_element_by_id("AddAssuranceForm_digest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_digest_input").send_keys(self.theHash)
        driver.find_element_by_id("AddAssuranceForm_email_input").clear()
        driver.find_element_by_id("AddAssuranceForm_email_input").send_keys(self.email)
        driver.find_element_by_id("AddAssuranceForm_assurance_input").clear()
        driver.find_element_by_id("AddAssuranceForm_assurance_input").send_keys('test')
        driver.find_element_by_id("AddAssuranceForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/adding_assurance.png")
        time.sleep(1)
        self.assertEqual(self.baseUrl  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("PopupWindow_MessageDiv").text
        self.assertEqual("message\nadded assurance test for {0}".format(self.email), body)
        return body


    def an_assurer_can_get_user_information_using_the_users_email(self, driver):
        driver.get(self.baseUrl  + "/static/login.html")
        driver.refresh()
        self.switchToTab("assurer")
        driver.find_element_by_id("ByEmailForm_email_input").clear()
        driver.find_element_by_id("ByEmailForm_email_input").send_keys(self.email)
        driver.find_element_by_id("ByEmailForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/get_user_data_by_email.png")
        time.sleep(1)
        self.assertEqual(self.baseUrl  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("PopupWindow_SuccessDiv").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.email))
        self.assertRegexpMatches(body, r"^[\s\S]*test[\s\S]*$")


    def _register_application(self):
        self.appsecret = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        appname = "app_{0}".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        self.redirectUri = 'https://demokracia.rulez.org/'
        applicationtool.do_main(0, appname, self.appsecret, self.redirectUri)
        app = Application.find(appname)
        self.appid = app.appid


    def if_you_are_logged_in_and_all_the_informations_are_correct_the_oauth_page_redirects_to_the_redirect_uri_with_your_authorization_code_as_parameter(self, driver):
        uri = '/v1/oauth2/auth'
        query_string = '?response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, self.redirectUri)
        fulluri = self.baseUrl + uri + query_string
        driver.get(fulluri)
        time.sleep(1)
        self.assertTrue(driver.current_url.startswith(self.redirectUri))
        self.code = driver.current_url.split('=')[1]

    def _weAreTheServerFromNow(self):
        self.http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=config.ca_certs,
        )

    def the_server_can_get_your_access_tokens_using_your_authorization_code(self):
        fields = dict(code=self.code,
            grant_type='authorization_code',
            client_id=self.appid,
            client_secret=self.appsecret,
            redirect_uri=self.redirectUri)
        url = self.baseUrl + "/v1/oauth2/token"
        resp = self.http.request("POST", url, fields=fields)
        self.assertEquals(resp.status, 200)
        answer = json.loads(resp.data)
        self.assertEqual(answer['token_type'], "Bearer")
        self.assertEqual(answer['expires_in'], 3600)
        self.accessToken = answer['access_token']
        self.refreshToken = answer['refresh_token']

    def the_server_can_get_your_user_info_with_your_access_token(self):
        headers = dict(Authorization='Bearer {0}'.format(self.accessToken))
        resp = self.http.request("get", self.baseUrl + "/v1/users/me", headers=headers)
        answer = json.loads(resp.data)
        self.assertEqual(answer['email'], self.assurerEmail)
        self.assertTrue(answer['assurances']['assurer'][0]['assurer'], self.assurerEmail)

    @test
    def _registration(self):
        driver = self.driver
        self.if_you_are_not_logged_in__the_authorization_uri_redirects_to_login_page_such_that_after_login_you_can_continue(driver)
        self.registration_is_done_by_filling_out_the_registration_form(driver)
        self._register_assurer(driver)
        assurancetool.do_main(0, self.assurerEmail, 'self', ["assurer", "assurer.test"])
        self.you_can_check_your_data_in_the_ME_url(driver)
        self.for_some_forms_you_need_a_csrf_token__you_can_obtain_it_by_logging_in(driver)
        self.an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(driver)
        self.an_assurer_can_get_user_information_using_the_users_email(driver)
        self._register_application()
        self.if_you_are_logged_in_and_all_the_informations_are_correct_the_oauth_page_redirects_to_the_redirect_uri_with_your_authorization_code_as_parameter(driver)
        self._weAreTheServerFromNow()
        self.the_server_can_get_your_access_tokens_using_your_authorization_code()
        self.the_server_can_get_your_user_info_with_your_access_token()

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
