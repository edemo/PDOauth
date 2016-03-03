from urllib import urlencode
from end2endtest import config
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pdoauth.models.User import User
from test.helpers.RandomUtil import RandomUtil
from FacebookUtil import FacebookUtil
import helpers.TestEnvironment as TE
import os
import re
from selenium.common.exceptions import TimeoutException
import time

class BrowsingUtil(RandomUtil, FacebookUtil):

    def goToLoginPage(self):
        TE.driver.get(TE.loginUrl)
        self.waitLoginPage()

    def closeMessage(self):
        self.wait_on_element_text(By.ID, "PopupWindow_CloseButton", "Close")
        TE.driver.find_element_by_id("PopupWindow_CloseButton").click()

    def wait_on_element_text(self, by_type, element, text):
        WebDriverWait(TE.driver, 20).until(
            EC.text_to_be_present_in_element(
                (by_type, element), text)
        )

    def wait_on_element(self, by_type, element):
        WebDriverWait(TE.driver, 20).until(
            EC.presence_of_element_located(
                (by_type, element))
        )

    def switchToTab(self,tab):
        TE.driver.find_element_by_id("{0}-menu".format(tab)).click()

    def callOauthUri(self):
        oauthUri = "{0}/v1/oauth2/auth?{1}".format(TE.backendUrl, urlencode({
                    "response_type":"code", 
                    "client_id":TE.app.appid, 
                    "redirect_uri":TE.app.redirect_uri}))
        TE.driver.get(oauthUri)
        self.waitLoginPage()
        uri = "{0}/static/login.html?{1}".format(TE.baseUrl, urlencode({"next":oauthUri}))
        self.assertEqual(uri, TE.driver.current_url)

    def waitFortestAppRedirectUri(self):
        return self.wait_on_element_text(By.TAG_NAME, "h1", "404")

    def assertReachedRedirectUri(self):
        self.waitFortestAppRedirectUri()
        currentUri = TE.driver.current_url
        expectedUri = TE.app.redirect_uri.lower()
        self.assertTrue(currentUri.startswith(expectedUri))

    def waitForWindow(self):
        timeCount = 1;
        while (len(TE.driver.window_handles) == 1 ):
            timeCount += 1
            time.sleep(1)
            if ( timeCount > 5 ): 
                raise TimeoutException()
        

    def swithToPopUp(self):
        for handle in TE.driver.window_handles:
            if handle != self.master:
                TE.driver.switch_to.window(handle)

    def waitLoginPage(self):
        return self.wait_on_element_text(By.ID, "msg", "")

    def registerUser(self):
        self.switchToTab('registration')
        self.setupUserCreationData()
        TE.driver.find_element_by_id("RegistrationForm_identifier_input").clear()
        TE.driver.find_element_by_id("RegistrationForm_identifier_input").send_keys(self.userCreationUserid)
        TE.driver.find_element_by_id("RegistrationForm_secret_input").clear()
        TE.driver.find_element_by_id("RegistrationForm_secret_input").send_keys(self.usercreationPassword)
        TE.driver.find_element_by_id("RegistrationForm_email_input").clear()
        TE.driver.find_element_by_id("RegistrationForm_email_input").send_keys(self.userCreationEmail)
        TE.driver.find_element_by_id("RegistrationForm_submitButton").click()

    def registerFreshUser(self):
        self.goToLoginPage()
        self.registerUser()
        self.closeMessage()

    def pushMeAndGatherResponse(self):
        self.switchToTab("account")
        TE.driver.find_element_by_id("melink").click()
        body = TE.driver.find_element_by_id("me_Msg").text
        return body

    def assertTextInMeMsg(self, textToFind):
        userdata = TE.driver.find_element_by_id("me_Msg").text
        self.assertTrue(textToFind in userdata)

    def saveQunitXml(self):
        self.wait_on_element_text(By.ID, "qunit-testresult", "failed")
        xml = TE.driver.find_element_by_id("qunit-xml").get_attribute("innerHTML")
        mypath = os.path.abspath(__file__)
        up = os.path.dirname
        xmlpath = os.path.join(up(up(up(up(mypath)))), "doc/screenshots/unittests.xml")
        xmlFile = open(xmlpath, "w")
        xmlFile.write(xml)
        xmlFile.close()

    def asertEnoughTestRanAndNoneFailed(self):
        body = TE.driver.find_element_by_id("qunit-testresult").text
        numtests = int(re.search("(\d+) assertions", body).groups()[0])
        failed = int(re.search("(\d+) failed", body).groups()[0])
        self.assertTrue(numtests > 40)
        self.assertTrue(failed == 0)

    def changeMyHash(self, digest=None):
        if digest is None:
            digest = self.createHash()
        self.switchToTab("account")
        TE.driver.find_element_by_id("ChangeHashForm_digest_input").clear()
        TE.driver.find_element_by_id("ChangeHashForm_digest_input").send_keys(digest)
        TE.driver.find_element_by_id("ChangeHashForm_submitButton").click()
        self.closeMessage()
        return digest


    def registerAndGiveHash(self):
        self.registerFreshUser()
        self.goToLoginPage()
        digest = self.createHash()
        self.changeMyHash(digest)
        return digest

    def logOut(self):
        self.goToLoginPage()
        element = TE.driver.find_element_by_id("tab-content-account")
        if element.is_displayed():
            self.switchToTab('account')
            TE.driver.find_element_by_id("logout_button").click()
        self.wait_on_element(By.ID, "tab-content-login")

    def tearDown(self):
        self.logOut()
        fbuser = User.getByEmail(config.facebookUser1.email)
        if fbuser:
            fbuser.rm()


    def obtainHash(self, identityNumber, motherName, formName):
        TE.driver.find_element_by_id(formName + "_predigest_input").clear()
        TE.driver.find_element_by_id(formName + "_predigest_input").send_keys(identityNumber)
        TE.driver.find_element_by_id(formName + "_predigest_mothername").clear()
        TE.driver.find_element_by_id(formName + "_predigest_mothername").send_keys(motherName)
        TE.driver.find_element_by_id(formName + "_getDigestButton").click()
        self.closeMessage()

    def assertHashFromFormEquals(self, formName, expectedSignature):
        digest = TE.driver.find_element_by_id(formName + "_digest_input").get_attribute('value')
        self.assertEqual(digest, expectedSignature)

    def loginWithPasswordAs(self, user):
        self.goToLoginPage()
        self.switchToTab('login')
        TE.driver.find_element_by_id("LoginForm_username_input").clear()
        TE.driver.find_element_by_id("LoginForm_username_input").send_keys(user.userName)
        TE.driver.find_element_by_id("LoginForm_password_input").clear()
        TE.driver.find_element_by_id("LoginForm_password_input").send_keys(user.password)
        TE.driver.find_element_by_id("LoginForm_submitButton").click()
        self.closeMessage()
