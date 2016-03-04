from twatson.unittest_annotations import Fixture, test
from helpers.BrowsingUtil import BrowsingUtil, TE
from test.helpers.CryptoTestUtil import CryptoTestUtil

class AssurerTest(Fixture,BrowsingUtil,CryptoTestUtil):

    @test
    def an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(self):
        digest=self.createHash()
        self.goToLoginPage()
        self.registerUser(digest=digest)
        self.logOut()
        self.loginWithPasswordAs(TE.assurerUser)
        self.assignAssurance(digest, self.userCreationEmail)
        expectedText = "message\nadded assurance test for {0}".format(self.userCreationEmail)
        self.assertPopupTextIs(expectedText)

    @test
    def an_assurer_can_get_user_information_using_the_users_email(self):
        self.goToLoginPage()
        self.registerUser()
        self.logOut()
        self.loginWithPasswordAs(TE.assurerUser)
        customerEmail = self.userCreationEmail
        self.getCustomerInfo(customerEmail)
        self.assertPopupMatchesRe(r"^[\s\S]*{0}[\s\S]*$".format(self.userCreationEmail))

    def tearDown(self):
        BrowsingUtil.tearDown(self)
