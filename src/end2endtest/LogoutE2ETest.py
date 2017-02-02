from helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase
import pdb

class LogoutE2ETest(TestCase,BrowsingUtil):

    def test_the_user_can_set_the_allow_autologaut_and_autologaut_logs_the_user_out(self):
        baseUrl = TE.baseUrl
        user = self.getAssurerUser()
        self.loginWithPasswordAndSubmitAs(user)
        self.switchToSection("settings")
        self.untickCheckbox("allow_app_sso_autologout")
        TE.driver.get(baseUrl + "/static/logout.html")
        self.waitUntilElementEnabled("flag")
        TE.driver.get(baseUrl + "/static/fiokom.html")
        self.waitUntilElementEnabled("nav-bar-my_account")
        self.switchToSection("settings")
        self.tickCheckbox("allow_app_sso_autologout")
        TE.driver.get(baseUrl + "/static/logout.html")
        self.waitUntilElementEnabled("flag")
        TE.driver.get(baseUrl + "/static/fiokom.html")
        self.waitUntilElementEnabled("nav-bar-login")
        self.logOut()
