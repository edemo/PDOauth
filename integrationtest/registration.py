from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, random, string, json, sys
import assurancetool

class Registration(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:8888/"
        self.verificationErrors = []
    
    def test_registration(self):
        driver = self.driver
        email ="a-{0}@example.com".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys("xxxxxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys("testuser")
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys("testtest")
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        
        assurer_email ="a-{0}@example.com".format(''.join(random.choice(string.ascii_letters) for _ in range(6)))
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        driver.find_element_by_id("RegistrationForm_digest_input").send_keys("xxxxxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys("testassurer")
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys("testtest")
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(assurer_email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        assurancetool.do_main(2, assurer_email,'self',["assurer", "assurer.test"])
        
        driver.get("http://127.0.0.1:8888/v1/users/me")
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/v1/users/me", driver.current_url)
        body = driver.find_element_by_css_selector("BODY").text
        self.assertRegexpMatches(body, r"^[\s\S]*assurances[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")
        
        driver.get(self.base_url+"static/login.html")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys("testassurer")
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys("testtest")
        driver.find_element_by_id("LoginForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(assurer_email))
        self.assertRegexpMatches(body, r"^[\s\S]*assurer[\s\S]*$")
        self.assertRegexpMatches(body, r"^[\s\S]*assurer.test[\s\S]*$")

        driver.find_element_by_id("AddAssuranceForm_digest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_digest_input").send_keys("xxxxxxxxxxxxxxxxx")
        driver.find_element_by_id("AddAssuranceForm_email_input").clear()
        driver.find_element_by_id("AddAssuranceForm_email_input").send_keys(email)
        driver.find_element_by_id("AddAssuranceForm_assurance_input").clear()
        driver.find_element_by_id("AddAssuranceForm_assurance_input").send_keys('test')
        driver.find_element_by_id("AddAssuranceForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("message").text
        self.assertEqual("added assurance test for {0}".format(email),body)

        driver.find_element_by_id("ByEmailForm_email_input").clear()
        driver.find_element_by_id("ByEmailForm_email_input").send_keys(email)
        driver.find_element_by_id("ByEmailForm_submitButton").click()
        time.sleep(1)
        self.assertEqual("http://127.0.0.1:8888/static/login.html", driver.current_url)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*{0}[\s\S]*$".format(email))
        self.assertRegexpMatches(body, r"^[\s\S]*test[\s\S]*$")

    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
