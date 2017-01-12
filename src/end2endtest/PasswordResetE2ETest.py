from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase


class PasswordResetE2ETest(TestCase,BrowsingUtil):

    def test_password_can_be_reset_using_the_reset_link(self):
        user = self.getAssurerUser()
        self.loginWithPasswordAndSubmitAs(user)
        self.assertElementMatchesRe("1","Adataim")
        self.logOut()
