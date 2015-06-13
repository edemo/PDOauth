from integrationtest.helpers.UserTesting import UserTesting
from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from end2endtest.helpers.BrowserSetup import BrowserSetup
from end2endtest import config

class EndUserTesting(Fixture, UserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    def fillInAndSubmitRegistrationForm(self, driver, email=None, userid=None, password=None, digest=None):
        if email is None:
            email=self.usercreation_email
        if userid is None:
            userid=self.usercreation_userid
        if password is None:
            password=self.usercreation_password
        if digest is None:
            digest = self.createHash()
        driver.find_element_by_id("RegistrationForm_digest_input").clear()
        if digest is not False:
            driver.find_element_by_id("RegistrationForm_digest_input").send_keys(digest)
        driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(userid)
        driver.find_element_by_id("RegistrationForm_secret_input").clear()
        driver.find_element_by_id("RegistrationForm_secret_input").send_keys(password)
        driver.find_element_by_id("RegistrationForm_email_input").clear()
        driver.find_element_by_id("RegistrationForm_email_input").send_keys(email)
        driver.find_element_by_id("RegistrationForm_submitButton").click()
    
