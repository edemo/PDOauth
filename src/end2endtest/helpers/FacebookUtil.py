from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
import end2endtest.helpers.TestEnvironment as TE
from selenium.webdriver.common.by import By
from end2endtest import config
from pdoauth.models.AppMap import AppMap

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
            for appMap in AppMap.getForUser(self.user):
                appMap.rm()
            self.user.rm()

    def handleFbLoginPage(self, user=None):
        self.master = TE.driver.current_window_handle
        self.waitForWindow()
        self.swithToPopUp()
        self.fillInFbPopUp(user)
        TE.driver.switch_to.window(self.master)

    def handleFbLogin(self, user=None):
        self.click("Facebook_registration_button")
        self.handleFbLoginPage(user)
        self.waitLoginPage()

    def handleFbRegistration(self, user=None):
        self.switchToTab('register')
        self.click("registration-form-method-selector-fb")
        self.handleFbLoginPage(user)
        self.waitLoginPage()
        self.tickCheckbox("registration-form_confirmField")
        self.click("registration-form_submitButton")

    def handleFbRegistrationAppLogin(self, user=None):
        self.click("register")
        self.click("registration-form-method-selector-fb")
        self.handleFbLoginPage(user)
        self.tickCheckbox("registration-form_confirmField")
        self.click("registration-form_submitButton")

    def logoutFromFacebook(self):
        TE.driver.get("https://facebook.com")
        TE.driver.delete_all_cookies()

    def assertFbUserIsLoggedIn(self, user=None):
        if user is None:
            user = config.facebookUser2
        self.assertElementMatchesRe("1","Adataim")
