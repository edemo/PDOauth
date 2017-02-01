from helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase


class LogoutE2ETest(TestCase,BrowsingUtil):

    def test_login_using_enter(self):
        user = self.getAssurerUser()
        self.loginWithPasswordAndSubmitAs(user)
        self.switchToSection("settings")
        self.tickCheckbox("allow_app_sso_autologout")
        TE.driver.get(basUrl + "/static/logout.html")
        waitUntilElementEnabled("flag")
        TE.driver.get(basUrl + "/static/fiokom.html")
        waitUntilElementEnabled("nav-bar-my_account")
        self.switchToSection("settings")
        self.tickCheckbox("allow_app_sso_autologout")
        TE.driver.get(basUrl + "/static/logout.html")
        waitUntilElementEnabled("flag")
        TE.driver.get(basUrl + "/static/fiokom.html")
        waitUntilElementEnabled("nav-bar-login")
        self.logOut()
