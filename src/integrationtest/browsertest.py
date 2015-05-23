from selenium import webdriver
import unittest, time
import config
from twatson.unittest_annotations import Fixture, test
import re
import os

class JavaScriptUnitTest(Fixture):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
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

if __name__ == "__main__":
    unittest.main()
