from selenium import webdriver
import unittest, time
from uuid import uuid4
from test.TestUtil import UserTesting
from pdoauth.app import app, mail
from bs4 import BeautifulSoup

class PasswordReset(unittest.TestCase, UserTesting):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "http://127.0.0.1:8888/"
        self.verificationErrors = []
        self.createUserWithCredentials()

    def getResetLink(self):
        with app.test_client() as c:
            with mail.record_messages() as outbox:
                c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
                text = outbox[0].body
                soup = BeautifulSoup(text)
                passwordResetLink = soup.find("a")['href']
        return passwordResetLink

    def test_password_reset(self):
        resetLink = self.getResetLink()
        driver = self.driver
        print resetLink
        driver.get(resetLink)
        driver.find_element_by_id("PasswordResetForm_password_input").clear()
        newPassword = unicode(uuid4())
        driver.find_element_by_id("PasswordResetForm_password_input").send_keys(newPassword)
        driver.find_element_by_id("PasswordResetForm_submitButton").click()
        time.sleep(1)
        body = driver.find_element_by_id("message").text
        self.assertEqual("Password successfully changed", body)
        
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
