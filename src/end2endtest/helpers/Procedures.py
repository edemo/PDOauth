import end2endtest.helpers.TestEnvironment as TE

class Procedures(object):

    def logOut(self):
        self.beginProcess("logout")
        self.goToLoginPage()
        element = TE.driver.find_element_by_id("nav-bar-my_account")
        displayed=element.value_of_css_property('display')
        if displayed=="block":
            self.switchToTab('my_account')
            self.click("logout_button")
        self.endProcess("logout")

    def loginWithPasswordAs(self, user):
        self.beginProcess("login with password")
        self.goToLoginPage()
        self.switchToTab('login')
        self.fillInField("LoginForm_email_input",user.userName)
        self.fillInField("LoginForm_password_input",user.password)
        self.click("LoginForm_submitButton")
        self.endProcess("login with password")

    def assignAssurance(self, digest, clientEmail):
        self.beginProcess("assign assurance to customer")
        self.switchToTab("assurer")
        self.fillInField("AddAssuranceForm_digest_input",digest)
        self.fillInField("AddAssuranceForm_email_input",clientEmail)
        self.fillInField("AddAssuranceForm_assurance_input",'test')
        self.click("AddAssuranceForm_submitButton")
        self.waitForMessage()
        self.endProcess("assign assurance to customer")

    def getCustomerInfo(self, customerEmail):
        self.beginProcess("get customer information")
        self.switchToTab("assurer")
        self.fillInField("ByEmailForm_email_input",customerEmail)
        self.click("ByEmailForm_submitButton")
        self.waitForMessage()
        self.endProcess("get customer information")

    def initiatePasswordReset(self, emailAddress):
        self.beginProcess("initiate password reset")
        self.fillInField("PasswordResetInitiateForm_OnLoginTab_email_input",emailAddress)
        self.click("PasswordResetInitiateForm_OnLoginTab_submitButton")
        self.closeMessage()
        self.endProcess("initiate password reset")

    def clickPasswordResetLink(self, password, passwordResetLink):
        self.beginProcess("click password reset link")
        TE.driver.get(passwordResetLink)
        self.fillInField("PasswordResetForm_OnLoginTab_password_input",password)
        self.click("PasswordResetForm_OnLoginTab_submitButton")
        self.closeMessage()
        self.endProcess("click password reset link")

    def registerUser(self, digest=None):
        self.beginProcess("register with password")
        self.switchToTab('registration')
        self.setupUserCreationData()
        self.fillInField("RegistrationForm_identifier_input", self.userCreationUserid)
        self.fillInField("RegistrationForm_secret_input", self.usercreationPassword)
        self.fillInField("RegistrationForm_email_input", self.userCreationEmail)
        if digest:
            self.fillInField("RegistrationForm_digest_input", digest)
        self.click("RegistrationForm_submitButton")
        self.endProcess("register with password")

    def changeMyHash(self, digest=None):
        self.beginProcess("change your hash")
        if digest is None:
            digest = self.createHash()
        self.switchToTab("account")
        self.fillInField("ChangeHashForm_digest_input", digest)
        self.click("ChangeHashForm_submitButton")
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
        self.closeMessage()
        self.endProcess("obtain hash")

