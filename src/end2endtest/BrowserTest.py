from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
import time

class BrowserTest(Fixture,BrowsingUtil):
    @test
    def javascript_end_to_end_tests_run_nicely(self):
        self.goToTestPage()
        self.click("e2e")
        self.saveQunitXml("e2e")
        TE.driver.save_screenshot("doc/screenshots/unit_tests-e2e.png")
        self.assertEnoughTestRanAndNoneFailed(1)

    @test
    def javascript_old_tests_run_nicely(self):
        self.goToTestPage()
        self.click("old-login")
        time.sleep(3)
        self.click("old-login")
        self.saveQunitXml("old-login")
        TE.driver.save_screenshot("doc/screenshots/unit_tests-old-login.png")
        self.assertEnoughTestRanAndNoneFailed(42)

    #@test
    def the_me_link_works(self):
        self.registerFreshUser()
        body = self.pushMeAndGatherResponse()
        self.assertRegexpMatches(body, r"^[\s\S]*@example.com[\s\S]*$")

    def tearDown(self):
        BrowsingUtil.tearDown(self)
