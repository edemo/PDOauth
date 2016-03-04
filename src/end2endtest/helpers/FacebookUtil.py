from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
import end2endtest.helpers.TestEnvironment as TE
from selenium.webdriver.common.by import By
from end2endtest import config

class FacebookUtil(object):
    def fillInFbPopUp(self, user=None):
        if user is None:
            user = config.facebookUser2
        self.wait_on_element(By.ID,"pass")
        self.fillInField("pass",user.password)
        self.fillInField("email",user.email)
        self.click("u_0_2")

    def removeFbuser(self,user=None):
        if user is None:
            user = config.facebookUser2
        self.user = User.getByEmail(user.email)
        if self.user:
            Credential.getByUser(self.user, "facebook").rm()
            self.user.rm()

    def handleFbLoginPage(self, user=None):
        self.master = TE.driver.current_window_handle
        self.waitForWindow()
        self.swithToPopUp()
        self.fillInFbPopUp(user)
        TE.driver.switch_to.window(self.master)
        self.waitLoginPage()

    def handleFbLogin(self, user=None):
        self.click("Facebook_registration_button")
        self.handleFbLoginPage(user)

    def handleFbRegistration(self, user=None):
        self.switchToTab('registration')
        self.click("Facebook_registration_button")
        self.handleFbLoginPage(user)

    def logoutFromFacebook(self):
        TE.driver.get("https://facebook.com")
        TE.driver.delete_all_cookies()

    def assertFbUserIsLoggedIn(self, user=None):
        if user is None:
            user = config.facebookUser2
        self.assertTextPresentInSuccessDiv(config.facebookUser2.email)
        self.closePopup()
