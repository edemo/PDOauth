from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase

class BrowserTest(TestCase,BrowsingUtil):
    
    def test_javascript_end_to_end_tests_run_nicely(self):
        self.goToTestPage()
        self.click("e2e")
        self.saveQunitXml("e2e")
        TE.driver.save_screenshot("doc/screenshots/unit_tests-e2e.png")
        self.assertEnoughTestRanAndNoneFailed(1)

    def tearDown(self):
        BrowsingUtil.tearDown(self)
