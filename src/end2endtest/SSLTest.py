from twatson.unittest_annotations import Fixture, test
from helpers.BrowsingUtil import BrowsingUtil,TE
import time
from selenium.webdriver.common.by import By

class SSLTest(Fixture,BrowsingUtil):

    def registerWithSSL(self):
        self.goToLoginPage()
        self.switchToTab("registration")
        self.setupUserCreationData()
        self.fillInField("KeygenForm_email_input", self.userCreationEmail)
        self.click("KeygenForm_submit")
        time.sleep(3)

    @test
    def you_can_register_using_ssl_and_login_with_the_certificate(self):
        self.registerWithSSL()
        self.goToSSLLoginPage() #FIXME: this should have happened automatically
        self.wait_on_element_text(By.ID, "me_Msg", self.userCreationEmail)
        self.assertTextInMeMsg(self.userCreationEmail)

    @test
    def you_can_add_an_ssl_login_to_your_account_and_login_with_your_certificate(self):
        self.registerFreshUser()
        self.switchToTab("account")
        self.fillInField("AddSslCredentialForm_email_input", self.userCreationEmail)
        self.click("AddSslCredentialForm_submit")
        time.sleep(3)
        self.logOut()
        self.goToSSLLoginPage()
        self.wait_on_element_text(By.ID, "me_Msg", self.userCreationEmail)
        self.assertTextInMeMsg(self.userCreationEmail)

    def tearDown(self):
        TE.newBrowser()