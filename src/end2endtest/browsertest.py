import unittest, time
import config
import re
import os
from end2endtest.helpers.EndUserTesting import EndUserTesting, test

class JavaScriptUnitTest(EndUserTesting):
    def setUp(self):
        self.setupDriver()
        self.base_url = config.Config.BASE_URL
        self.verificationErrors = []

    @test
    def javascript_unit_test_run_nicely(self):
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        driver.find_element_by_id("Unit_test_button").click()
        time.sleep(2)
        mypath = os.path.abspath(__file__)
        up = os.path.dirname
        xmlpath = os.path.join(up(up(up(mypath))), "doc/screenshots/unittests.xml")

        driver.save_screenshot("doc/screenshots/unit_tests.png")
        xml = driver.find_element_by_id("qunit-xml").get_attribute("innerHTML")
        f = open(xmlpath,"w")
        f.write(xml)
        f.close()
        body = driver.find_element_by_id("qunit-testresult").text
        numtests = int(re.search("(\d+) assertions",body).groups()[0])
        failed = int(re.search("(\d+) failed",body).groups()[0])
        self.assertTrue(numtests > 40)
        self.assertTrue(failed == 0)
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    @test
    def the_me_link_works(self):
        driver = self.driver
        driver.get(self.base_url+"/static/login.html")
        user = self.createUserWithCredentials()
        user.activate()
        self.thePassword = self.mkRandomPassword()
        self.switchToTab("login")
        driver.find_element_by_id("LoginForm_username_input").clear()
        driver.find_element_by_id("LoginForm_username_input").send_keys(self.usercreation_userid)
        driver.find_element_by_id("LoginForm_password_input").clear()
        driver.find_element_by_id("LoginForm_password_input").send_keys(self.usercreation_password)
        driver.find_element_by_id("LoginForm_submitButton").click()
        time.sleep(1)
        driver.get(self.base_url+"/static/login.html")
        body = driver.find_element_by_id("userdata").text
        self.assertEqual(body, '')
        self.switchToTab("account")
        driver.find_element_by_id("melink").click()
        time.sleep(5)
        body = driver.find_element_by_id("userdata").text
        self.assertRegexpMatches(body, r"^[\s\S]*@example.com[\s\S]*$")


if __name__ == "__main__":
    unittest.main()
