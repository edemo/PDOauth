from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase


class LoginE2ETest(TestCase,BrowsingUtil):

    def test_login_using_enter(self):
        user = self.getAssurerUser()
        self.loginWithPasswordAndSubmitAs(user)
        self.assertElementMatchesRe("1","Adataim")
        self.logOut()
