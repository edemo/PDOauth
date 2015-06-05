import unittest, time
from pdoauth.app import app, mail
from bs4 import BeautifulSoup
from twatson.unittest_annotations import Fixture, test
import config
from end2endtest.BrowserSetup import BrowserSetup
from test.helpers.todeprecate.UserTesting import UserTesting
from pdoauth import main  # @UnusedImport

class EndUserPasswordResetTest(Fixture, UserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []
        self.createUserWithCredentials()

    def the_reset_link_is_in_the_reset_email(self):
        with app.test_client() as c:
            with mail.record_messages() as outbox:
                c.get("/v1/users/{0}/passwordreset".format(self.usercreation_email))
                text = outbox[0].body
                soup = BeautifulSoup(text)
                passwordResetLink = soup.find("a")['href']
        return passwordResetLink

    @test
    def password_can_be_reset_using_the_reset_link(self):
        resetLink = self.the_reset_link_is_in_the_reset_email()
        driver = self.driver
        driver.get(resetLink)
        self.switchToTab("account")
        driver.find_element_by_id("PasswordResetForm_password_input").clear()
        newPassword = self.mkRandomPassword()
        driver.find_element_by_id("PasswordResetForm_password_input").send_keys(newPassword)
        driver.find_element_by_id("PasswordResetForm_submitButton").click()
        driver.save_screenshot("doc/screenshots/using_password_reset.png")
        time.sleep(1)
        body = driver.find_element_by_id("message").text
        self.assertEqual("Password successfully changed", body)
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
