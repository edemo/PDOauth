import unittest
import config
from twatson.unittest_annotations import Fixture, test
from end2endtest.BrowserSetup import BrowserSetup
from end2endtest.EndUserTesting import EndUserTesting
from pdoauth.app import app
import time

class EndUserDigestManagementTest(Fixture, EndUserTesting, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def you_can_add_a_digest_as_a_logged_in_user(self):
        self.assertEqual(len(config.testSignatureAllOne),512)
        self.setupUserCreationData()
        self.driver.get(app.config.get("START_URL"))
        self.fillInAndSubmitRegistrationForm(driver=self.driver, digest=False)
        
        digest = self.createHash()
        self.switchToTab("account")
        self.driver.find_element_by_id("ChangeHashForm_digest_input").clear()
        self.driver.find_element_by_id("ChangeHashForm_digest_input").send_keys(digest)
        self.driver.find_element_by_id("ChangeHashForm_submitButton").click()
        time.sleep(1)
        userdata = self.driver.find_element_by_id("userdata").text
        self.assertTrue("hash: {0}".format(digest) in userdata)

    @test
    def you_can_change_the_digest_as_a_logged_in_user(self):
        self.assertEqual(len(config.testSignatureAllOne),512)
        self.setupUserCreationData()
        self.driver.get(app.config.get("START_URL"))
        oldDigest=self.createHash()
        self.fillInAndSubmitRegistrationForm(driver=self.driver, digest=oldDigest)
        time.sleep(1)
        userdata = self.driver.find_element_by_id("userdata").text
        self.assertTrue("hash: {0}".format(oldDigest) in userdata)
        self.setupRandom()
        digest = self.createHash()
        self.assertTrue(oldDigest != digest)
        self.switchToTab("account")
        self.driver.find_element_by_id("ChangeHashForm_digest_input").clear()
        self.driver.find_element_by_id("ChangeHashForm_digest_input").send_keys(digest)
        self.driver.find_element_by_id("ChangeHashForm_submitButton").click()
        time.sleep(1)
        userdata = self.driver.find_element_by_id("userdata").text
        self.assertTrue("hash: {0}".format(digest) in userdata)

    @test
    def you_can_delete_the_digest_as_a_logged_in_user_by_giving_empty_one(self):
        self.assertEqual(len(config.testSignatureAllOne),512)
        self.setupUserCreationData()
        self.driver.get(app.config.get("START_URL"))
        oldDigest=self.createHash()
        self.fillInAndSubmitRegistrationForm(driver=self.driver, digest=oldDigest)
        time.sleep(1)
        userdata = self.driver.find_element_by_id("userdata").text
        self.assertTrue("hash: {0}".format(oldDigest) in userdata)
        self.switchToTab("account")
        self.driver.find_element_by_id("ChangeHashForm_digest_input").clear()
        self.driver.find_element_by_id("ChangeHashForm_submitButton").click()
        time.sleep(1)
        userdata = self.driver.find_element_by_id("userdata").text
        self.assertTrue("hash: null" in userdata)
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
