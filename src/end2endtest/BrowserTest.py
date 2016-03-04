from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE

class BrowserTest(Fixture,BrowsingUtil):
    @test
    def javascript_unit_test_run_nicely(self):
        self.goToLoginPage()
        self.click("Unit_test_button")
        self.saveQunitXml()
        TE.driver.save_screenshot("doc/screenshots/unit_tests.png")
        self.assertEnoughTestRanAndNoneFailed()

    @test
    def the_me_link_works(self):
        self.registerFreshUser()
        body = self.pushMeAndGatherResponse()
        self.assertRegexpMatches(body, r"^[\s\S]*@example.com[\s\S]*$")

    def tearDown(self):
        BrowsingUtil.tearDown(self)
