import end2endtest.helpers.TestEnvironment as TE
from selenium.webdriver.common.by import By

class Procedures(object):

    def logOut(self):
        self.beginProcess("logout")
        self.goToLoginPage()
        element = TE.driver.find_element_by_id("nav-bar-logout")
        displayed=element.value_of_css_property('display')
        if displayed=="list-item":
            self.click("logout_button")
        self.waitLoginPage()
        self.endProcess("logout")

    def loginWithPasswordAs(self, user):
        self.beginProcess("login with password")
        self.goToLoginPage()
        self.switchToTab('login')
        self.fillInField("LoginForm_email_input",user.userName)
        self.fillInField("LoginForm_password_input",user.password)
        self.click("LoginForm_submitButton")
        self.endProcess("login with password")

    def loginWithPasswordAndSubmitAs(self, user):
        self.beginProcess("login with password and submit")
        self.goToLoginPage()
        self.switchToTab('login')
        self.fillInField("LoginForm_email_input", user.userName)
        self.fillInField("LoginForm_password_input", user.password)
        self.sendEnter("LoginForm_password_input")
        self.endProcess("login with password and submit")

    def assignAssurance(self, clientEmail, personalId, motherName):
        self.beginProcess("assign assurance to customer")
        self.switchToSection("assurer")
        self.obtainHash(personalId, motherName, "assurancing")
        self.wait_on_element_class(By.ID, 'assurance-giving_message', "given")
        self.fillInField("ByEmailForm_email_input",clientEmail)
        self.selectOptionValue("assurance-giving_assurance_selector", 'test')
        self.click("assurance-giving_submit-button")
        self.endProcess("assign assurance to customer")

    def getCustomerInfo(self, customerEmail):
        self.beginProcess("get customer information")
        self.switchToSection("assurer")
        self.fillInField("ByEmailForm_email_input",customerEmail)
        self.click("ByEmailForm_submitButton")
        self.waitForMessage2()
        self.endProcess("get customer information")

    def initiatePasswordReset(self, emailAddress):
        self.beginProcess("initiate password reset")
        self.fillInField("LoginForm_email_input",emailAddress)
        self.click("InitiatePasswordReset")
        self.closeMessage()
        self.endProcess("initiate password reset")

    def clickPasswordResetLink(self, password, passwordResetLink):
        self.beginProcess("click password reset link")
        TE.driver.get(passwordResetLink)
        self.fillInField("PasswordResetForm_password_input",password)
        self.click("PasswordResetForm_OnLoginTab_submitButton")
        self.closeMessage(closeWait=False)
        self.endProcess("click password reset link")

    def registerUser(self, digest=None, buttonId="nav-bar-register_a", personalId=None, motherName=None):
        self.beginProcess("register with password")
        self.click(buttonId)
        self.waitForTraces(["userIsNotLoggedIn"])
        self.waitUntilElementEnabled("registration-form_identifier_input")
        time.sleep(3)
        self.setupUserCreationData()
        self.fillInField("registration-form_identifier_input", self.userCreationUserid)
        self.fillInField("registration-form_secret_input", self.usercreationPassword)
        self.fillInField("registration-form_secret_backup", self.usercreationPassword)
        self.fillInField("registration-form_email_input", self.userCreationEmail)
        elementId = "registration-form_confirmField"
        self.tickCheckbox(elementId)
        if digest:
            self.fillInField("registration-form_digest_input", digest)
        if personalId:
            self.click("make_here")
            self.fillInField("registration-form_predigest_input", personalId)
            self.fillInField("registration-form_predigest_mothername", motherName)
            self.click("registration-form_getDigestButton")
            self.waitUntilElementHasText("registration-form_digest_input")
        self.click("registration-form_submitButton")
        if buttonId=="nav-bar-register_a":
            self.waitForTraces(["myappsCallback"])
        self.endProcess("register with password")

    def changeMyHash(self, digest=None):
        self.beginProcess("change your hash")
        if digest is None:
            digest = self.createHash()
        self.click("settings_section_link")
        print(TE.driver.execute_script("return document.getElementById('viewChangeHashForm').onclick.toString()"))
        print(self.getTraces())
        self.click("viewChangeHashForm")
        print(self.getTraces())
        self.fillInField("change-hash-form_digest_input", digest)
        self.click("changeHash")
        self.observeField("PopupWindow_SuccessDiv")
        self.closeMessage()
        self.endProcess("change your hash")
        return digest

    def pushMeAndGatherResponse(self):
        self.beginProcess("refresh user info displayed")
        self.switchToTab("account")
        self.click("melink")
        body = self.observeField("me_Msg")
        self.endProcess("refresh user info displayed")
        return body

    def obtainHash(self, identityNumber, motherName, formName):
        self.beginProcess("obtain hash")
        self.fillInField(formName + "_predigest_input", identityNumber)
        self.fillInField(formName + "_predigest_mothername", motherName)
        self.click(formName + "_getDigestButton")
        self.waitForTraces(["gotDigest"])
        self.endProcess("obtain hash")
