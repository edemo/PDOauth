from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import unittest, time
import config

class Hash(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "http://127.0.0.1:8888/"
        self.verificationErrors = []

    def test_registration(self):
        if (config.skipSlowTests):
            return
        driver = self.driver
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_predigest_input").clear()
        driver.find_element_by_id("RegistrationForm_predigest_input").send_keys("11111111110")
        driver.find_element_by_id("RegistrationForm_getDigestButton").click()
        time.sleep(1)
        digest = driver.find_element_by_id("RegistrationForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllOne)
        time.sleep(59)
        driver = self.driver
        driver.get("http://127.0.0.1:8888/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("AddAssuranceForm_predigest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_predigest_input").send_keys("22222222220")
        driver.find_element_by_id("AddAssuranceForm_getDigestButton").click()
        time.sleep(1)
        digest = driver.find_element_by_id("AddAssuranceForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllTwo)

    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
