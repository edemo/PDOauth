import unittest, time
import config
from end2endtest.helpers.EndUserTesting import EndUserTesting, test

class EndUserObtainingHashTest(EndUserTesting):

    @test
    def you_can_obtain_the_hash_by_filling_in_your_personal_id_and_pushing_the_button_near_it(self):
        """
        In this case your web browser goes directly to anchor.edemokraciagep.org, and gets the hash for you.
        The SSO server never sees your personal id.
        """
        if config.skipSlowTests:
            return
        driver = self.driver
        driver.get(self.backendUrl+"/static/login.html?next=/v1/users/me")
        self.switchToTab('registration')
        driver.find_element_by_id("RegistrationForm_predigest_input").clear()
        driver.find_element_by_id("RegistrationForm_predigest_input").send_keys("11111111110")
        driver.find_element_by_id("RegistrationForm_predigest_mothername").clear()
        driver.find_element_by_id("RegistrationForm_predigest_mothername").send_keys("Mother Test")
        driver.find_element_by_id("RegistrationForm_getDigestButton").click()
        time.sleep(1)
        driver.save_screenshot("doc/screenshots/getting_digest_for_registration.png")
        time.sleep(10)
        digest = driver.find_element_by_id("RegistrationForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllOne)


    @test
    def assurer_can_obtain_the_hash_by_filling_in_your_personal_id__mother_name_and_pushing_the_button_near_it(self):
        if config.skipSlowTests:
            return
        driver = self.driver
        self.loginAsAssurer(driver)

        driver.get(self.backendUrl+"/static/login.html?next=/v1/users/me")
        time.sleep(1)
        self.switchToTab('assurer')
        driver.find_element_by_id("AddAssuranceForm_predigest_input").clear()
        driver.find_element_by_id("AddAssuranceForm_predigest_input").send_keys("22222222220")
        driver.find_element_by_id("AddAssuranceForm_predigest_mothername").clear()
        driver.find_element_by_id("AddAssuranceForm_predigest_mothername").send_keys("Test Mother")
        driver.find_element_by_id("AddAssuranceForm_getDigestButton").click()
        time.sleep(5)
        driver.save_screenshot("doc/screenshots/getting_digest_for_assurance.png")
        digest = driver.find_element_by_id("AddAssuranceForm_digest_input").get_attribute('value')
        self.assertEqual(digest,config.testSignatureAllTwo)

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
