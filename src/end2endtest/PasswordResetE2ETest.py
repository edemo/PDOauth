from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
from unittest.case import TestCase


class PasswordResetE2ETest(TestCase,BrowsingUtil):

    def test_password_can_be_reset_using_the_reset_link(self):
        password = "Ez3gyJelsz0"
        user = self.getAssurerUser()
        self.doPasswordResetWithNewPassword(password)
        oldPassword=user.password
        user.password=password
        self.loginWithPasswordAs(user)
        self.assertElementMatchesRe("1","Adataim")
        self.logOut()
        TE.assurerUser.password=oldPassword
        self.doPasswordResetWithNewPassword(oldPassword)
