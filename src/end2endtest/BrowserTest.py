from twatson.unittest_annotations import Fixture
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
import time
import pdb

class BrowserTest(Fixture,BrowsingUtil):
    
    def test_javascript_end_to_end_tests_run_nicely(self):
        self.goToTestPage()
        self.click("e2e")
        self.saveQunitXml("e2e")
        TE.driver.save_screenshot("doc/screenshots/unit_tests-e2e.png")
        self.assertEnoughTestRanAndNoneFailed(1)

    
    def test_javascript_old_tests_run_nicely(self):
        self.goToTestPage()
        self.click("old-login")
        time.sleep(3)
        self.click("old-login")
        self.saveQunitXml("old-login")
        TE.driver.save_screenshot("doc/screenshots/unit_tests-old-login.png")
        self.assertEnoughTestRanAndNoneFailed(42)

    def tearDown(self):
        BrowsingUtil.tearDown(self)
