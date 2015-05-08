from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

class Login(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:8888/"
        self.verificationErrors = []
    
    def test_login(self):
        driver = self.driver
        driver.get(self.base_url+"static/login.html?next=/v1/users/me")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys("testuser")
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys("testtest")
        driver.find_element_by_id("LoginForm_submitButton").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
