import unittest, time
from pdoauth.app import app, mail
from bs4 import BeautifulSoup
from end2endtest.helpers.EndUserTesting import EndUserTesting, test
from pdoauth import main  # @UnusedImport

class EndUserPasswordResetTest(EndUserTesting):
    def setUp(self):
        EndUserTesting.setUp(self)
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
        self.switchToTab("login")
        driver.find_element_by_id("PasswordResetForm_OnLoginTab_password_input").clear()
        newPassword = self.mkRandomPassword()
        driver.find_element_by_id("PasswordResetForm_OnLoginTab_password_input").send_keys(newPassword)
        driver.find_element_by_id("PasswordResetForm_OnLoginTab_submitButton").click()
        driver.save_screenshot("doc/screenshots/using_password_reset.png")
        time.sleep(1)
        body = driver.find_element_by_id("PopupWindow_MessageDiv").text
        self.assertEqual("message\nPassword successfully changed", body)
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
