from end2endtest import config
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
import helpers.TestEnvironment as TE
from selenium.webdriver.common.by import By

class FacebookUtil(object):
    def fillInFbPopUp(self, user=None):
        if user is None:
            user = config.facebookUser2
        self.wait_on_element(By.ID,"pass")
        print user.email
        TE.driver.find_element_by_id("pass").clear()
        TE.driver.find_element_by_id("pass").send_keys(user.password)
        TE.driver.find_element_by_id("email").clear()
        TE.driver.find_element_by_id("email").send_keys(user.email)
        TE.driver.find_element_by_id("u_0_2").click()

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
        TE.driver.find_element_by_id("Facebook_registration_button").click()
        self.handleFbLoginPage(user)

    def handleFbRegistration(self, user=None):
        self.switchToTab('registration')
        TE.driver.find_element_by_id("Facebook_registration_button").click()
        self.handleFbLoginPage(user)

    def logoutFromFacebook(self):
        TE.driver.get("https://facebook.com")
        TE.driver.delete_all_cookies()

    def assertFbUserIsLoggedIn(self, user=None):
        if user is None:
            user = config.facebookUser2
        body = TE.driver.find_element_by_id("PopupWindow_SuccessDiv").text
        self.assertTrue(config.facebookUser2.email in body)
        self.closePopup()
