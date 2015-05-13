from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import unittest, time, random, string, json
import assurancetool
import applicationtool
from pdoauth.models.Application import Application
import urllib3

class Registration(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:8888/"
        self.verificationErrors = []
    

    def register_normal_user(self, driver, time):
        self.email = "a-{0}@example.com".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys("xxxxxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys("testuser")
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys("testtest")
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(self.email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")


    def redirext_before_login(self, driver):
        driver.get("http://127.0.0.1:8888/v1/oauth2/auth")
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)


    def register_assurer(self, driver, time):
        self.assurer_email = "a-{0}@example.com".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys("xxxxxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys("testassurer")
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys("testtest")
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(self.assurer_email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")


    def check_me(self, driver, time):
        driver.get("http://127.0.0.1:8888/v1/users/me")
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")


    def login_for_csrf(self, driver, time):
        driver.get(self.base_url + "static/login.html")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys("testassurer")
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys("testtest")
        driver.find_element_by_id("LoginForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.assurer_email))
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")
        return body


    def add_assurance(self, driver, time):
        driver.find_element_by_id("AddAssuranceForm_digest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_digest_input").send_keys("xxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("AddAssuranceForm_email_input").clear()
        driver.find_element_by_id("AddAssuranceForm_email_input").send_keys(self.email)
        driver.find_element_by_id("AddAssuranceForm_assurance_input").clear()
        driver.find_element_by_id("AddAssuranceForm_assurance_input").send_keys('test')
        driver.find_element_by_id("AddAssuranceForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("message").text
        self.assertEqual("added assurance test for {0}".format(self.email), body)
        return body


    def check_by_email(self, driver, time):
        driver.find_element_by_id("ByEmailForm_email_input").clear()
        driver.find_element_by_id("ByEmailForm_email_input").send_keys(self.email)
        driver.find_element_by_id("ByEmailForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(self.email))
        self.assertRegexpMatches(body, r"^[\s\S]*test[\s\S]*$")


    def register_application(self):
        self.appsecret = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        appname = "testapplication"
        self.redirect_uri = 'https://demokracia.rulez.org/'
        applicationtool.do_main(2, appname, self.appsecret, self.redirect_uri)
        app = Application.find(appname)
        self.appid = app.appid


    def do_oauth_auth(self, driver, time):
        uri = 'v1/oauth2/auth'
        query_string = '?response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, self.redirect_uri)
        fulluri = self.base_url + uri + query_string
        driver.get(fulluri)
        time.sleep(1)
        self.assertTrue(driver.current_url.startswith(self.redirect_uri))
        self.code = driver.current_url.split('=')[1]


    def get_token(self):
        resp = self.http.request("POST", self.base_url + "v1/oauth2/token", fields=dict(code=self.code, 
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


    def weAreTheServerFromNow(self):
        self.http = urllib3.PoolManager()


    def getUserInfoWithAccessToken(self):
        headers = dict(Authorization='Bearer {0}'.format(self.access_token))
        resp = self.http.request("get", self.base_url + "v1/users/me", headers=headers)
        answer = json.loads(resp.data)
        self.assertEqual(answer['email'], self.assurer_email)
        self.assertTrue(answer['assurances']['assurer'][0]['assurer'], self.assurer_email)

    def test_registration(self):
        driver = self.driver
        self.redirext_before_login(driver)
        self.register_normal_user(driver, time)
        self.register_assurer(driver, time)
        assurancetool.do_main(2, self.assurer_email, 'self', ["assurer", "assurer.test"])
        self.check_me(driver, time)
        self.login_for_csrf(driver, time)
        self.add_assurance(driver, time)
        self.check_by_email(driver, time)
        self.register_application()
        self.do_oauth_auth(driver, time)
        self.weAreTheServerFromNow()
        self.get_token()
        self.getUserInfoWithAccessToken()
        
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
