from helpers.BrowsingUtil import BrowsingUtil, TE
from test.helpers.CryptoTestUtil import CryptoTestUtil
from unittest.case import TestCase

class AssurerTest(TestCase,BrowsingUtil,CryptoTestUtil):
        
    
    def test_an_assurer_can_add_assurance_to_other_users_using_the_assurance_form(self):
        self.goToRegisterPage()
        personalId = "11111111110"
        motherName = self.mkRandomString(10)
        self.registerUser(personalId=personalId, motherName=motherName)
        self.logOut()
        self.loginWithPasswordAs(TE.assurerUser)
        self.assignAssurance(self.userCreationEmail, personalId, motherName)
        expectedText = u'A test igazolást a {0} felhasználó számára kiadtuk.'.format(self.userCreationEmail.lower())
        self.waitForMessage2()
        self.assertPopupTextIs(expectedText)

    
    def test_an_assurer_can_get_user_information_using_the_users_email(self):
        self.goToRegisterPage()
        self.registerUser()
        self.logOut()
        self.loginWithPasswordAs(TE.assurerUser)
        customerEmail = self.userCreationEmail
        self.getCustomerInfo(customerEmail)
        self.assertPopupMatchesRe(r"Felhaszn")

    def tearDown(self):
        BrowsingUtil.tearDown(self)
