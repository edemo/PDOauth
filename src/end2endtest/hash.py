import unittest, time
import config
from twatson.unittest_annotations import Fixture, test
from end2endtest.BrowserSetup import BrowserSetup

class EndUserObtainingHashTest(Fixture, BrowserSetup):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def you_can_obtain_the_hash_by_filling_in_your_personal_id_and_pushing_the_button_near_it(self):
        """
        In this case your web browser goes directly to anchor.edemokraciagep.org, and gets the hash for you.
        The SSO server never sees your personal id.
        """
        if (config.skipSlowTests):
            return
        driver = self.driver
        driver.get(self.base_url+"/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("RegistrationForm_predigest_input").clear()
        driver.find_element_by_id("RegistrationForm_predigest_input").send_keys("11111111110")
        driver.find_element_by_id("RegistrationForm_getDigestButton").click()
        driver.save_screenshot("doc/screenshots/getting_digest_for_registration.png")
        time.sleep(1)
        digest = driver.find_element_by_id("RegistrationForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllOne)
        time.sleep(59)
        driver = self.driver
        driver.get(self.base_url+"/static/login.html?next=/v1/users/me")
        driver.find_element_by_id("AddAssuranceForm_predigest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_predigest_input").send_keys("22222222220")
        driver.find_element_by_id("AddAssuranceForm_getDigestButton").click()
        time.sleep(1)
        driver.save_screenshot("doc/screenshots/getting_digest_for_assurance.png")
        digest = driver.find_element_by_id("AddAssuranceForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllTwo)
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
