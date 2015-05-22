from selenium import webdriver
import unittest, time, random, string, json
import assurancetool
import applicationtool
from pdoauth.models.Application import Application
import urllib3
from twatson.unittest_annotations import Fixture, test
import config
from urllib import urlencode
from test.TestUtil import UserTesting

class EndUserRegistrationTest(Fixture, UserTesting):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.base_url = "http://"+ config.Config.SERVER_NAME
        self.verificationErrors = []
        randomString = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        self.email = "a-{0}@example.com".format(randomString)
        self.normaluser = "normaluser{0}".format(randomString)
        self.assurer = "assurer{0}".format(randomString)
        self.assurer_email = "a-{0}@example.com".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
    

    def registration_is_done_by_filling_out_the_registration_form(self, driver, time):
        driver.get(self.base_url  + "/static/login.html?next=/v1/users/me")
        driver.refresh()
        self.setupRandom()
        self.thePassword = self.mkRandomPassword()
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys(self.createHash())
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(self.normaluser)
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys(self.thePassword)
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(self.email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/registration.png")
        time.sleep(1)
        self.assertEqual(self.base_url  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")

    def if_you_are_not_logged_in__the_authorization_uri_redirects_to_login_page_such_that_after_login_you_can_continue(self, driver):
        uri = self.base_url + "/v1/oauth2/auth"
        driver.get(uri)
        driver.refresh()
        time.sleep(1)
        targetUri = "{0}/static/login.html?{1}".format(
            self.base_url,
            urlencode({"next": uri}))
        self.assertEqual(targetUri, driver.current_url)


    def _register_assurer(self, driver, time):
        driver.get(self.base_url  + "/static/login.html?next=/v1/users/me")
        driver.refresh()
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys(self.createHash())
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(self.assurer)
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys(self.thePassword)
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(self.assurer_email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(1)
        self.assertEqual(self.base_url  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")


    def you_can_check_your_data_in_the_ME_url(self, driver, time):
        driver.get(self.base_url  + "/v1/users/me")
        driver.save_screenshot("doc/screenshots/my_data.png")
        time.sleep(1)
        self.assertEqual(self.base_url  + "/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")


    def for_some_forms_you_need_a_csrf_token__you_can_obtain_it_by_logging_in(self, driver, time):
        driver.get(self.base_url + "/static/login.html")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys(self.assurer)
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys(self.thePassword)
        driver.find_element_by_id("LoginForm_submitButton").click()
        time.sleep(1)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.assurer_email))
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")
        return body


    def an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(self, driver, time):
        driver.get(self.base_url  + "/static/login.html")
        driver.refresh()
        driver.find_element_by_id("AddAssuranceForm_digest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_digest_input").send_keys(self.createHash())
        driver.find_element_by_id("AddAssuranceForm_email_input").clear()
        driver.find_element_by_id("AddAssuranceForm_email_input").send_keys(self.email)
        driver.find_element_by_id("AddAssuranceForm_assurance_input").clear()
        driver.find_element_by_id("AddAssuranceForm_assurance_input").send_keys('test')
        driver.find_element_by_id("AddAssuranceForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/adding_assurance.png")
        time.sleep(1)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("message").text
        self.assertEqual("added assurance test for {0}".format(self.email), body)
        return body


    def an_assurer_can_get_user_information_using_the_users_email(self, driver, time):
        driver.get(self.base_url  + "/static/login.html")
        driver.refresh()
        driver.find_element_by_id("ByEmailForm_email_input").clear()
        driver.find_element_by_id("ByEmailForm_email_input").send_keys(self.email)
        driver.find_element_by_id("ByEmailForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/get_user_data_by_email.png")
        time.sleep(1)
        self.assertEqual(self.base_url  + "/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.email))
        self.assertRegexpMatches(body, r"^[\s\S]*test[\s\S]*$")


    def _register_application(self):
        self.appsecret = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        appname = "app_{0}".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        self.redirect_uri = 'https://demokracia.rulez.org/'
        applicationtool.do_main(2, appname, self.appsecret, self.redirect_uri)
        app = Application.find(appname)
        self.appid = app.appid


    def if_you_are_logged_in_and_all_the_informations_are_correct_the_oauth_page_redirects_to_the_redirect_uri_with_your_authorization_code_as_parameter(self, driver, time):
        uri = '/v1/oauth2/auth'
        query_string = '?response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, self.redirect_uri)
        fulluri = self.base_url + uri + query_string
        driver.get(fulluri)
        time.sleep(1)
        self.assertTrue(driver.current_url.startswith(self.redirect_uri))
        self.code = driver.current_url.split('=')[1]

    def _weAreTheServerFromNow(self):
        self.http = urllib3.PoolManager()


    def the_server_can_get_your_access_tokens_using_your_authorization_code(self):
        resp = self.http.request("POST", self.base_url + "/v1/oauth2/token", fields=dict(code=self.code, 
                grant_type='authorization_code', 
                client_id=self.appid, 
                client_secret=self.appsecret, 
                redirect_uri=self.redirect_uri))
        self.assertEquals(resp.status, 200)
        answer = json.loads(resp.data)
        self.assertEqual(answer['token_type'], "Bearer")
        self.assertEqual(answer['expires_in'], 3600)
        self.access_token = answer['access_token']
        self.refresh_token = answer['refresh_token']


    def the_server_can_get_your_user_info_with_your_access_token(self):
        headers = dict(Authorization='Bearer {0}'.format(self.access_token))
        resp = self.http.request("get", self.base_url + "/v1/users/me", headers=headers)
        answer = json.loads(resp.data)
        self.assertEqual(answer['email'], self.assurer_email)
        self.assertTrue(answer['assurances']['assurer'][0]['assurer'], self.assurer_email)

    @test
    def _registration(self):
        driver = self.driver
        self.if_you_are_not_logged_in__the_authorization_uri_redirects_to_login_page_such_that_after_login_you_can_continue(driver)
        self.registration_is_done_by_filling_out_the_registration_form(driver, time)
        self._register_assurer(driver, time)
        assurancetool.do_main(2, self.assurer_email, 'self', ["assurer", "assurer.test"])
        self.you_can_check_your_data_in_the_ME_url(driver, time)
        self.for_some_forms_you_need_a_csrf_token__you_can_obtain_it_by_logging_in(driver, time)
        self.an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(driver, time)
        self.an_assurer_can_get_user_information_using_the_users_email(driver, time)
        self._register_application()
        self.if_you_are_logged_in_and_all_the_informations_are_correct_the_oauth_page_redirects_to_the_redirect_uri_with_your_authorization_code_as_parameter(driver, time)
        self._weAreTheServerFromNow()
        self.the_server_can_get_your_access_tokens_using_your_authorization_code()
        self.the_server_can_get_your_user_info_with_your_access_token()
        
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
