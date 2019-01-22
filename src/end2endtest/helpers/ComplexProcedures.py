import end2endtest.helpers.TestEnvironment as TE
from pdoauth.models.Credential import Credential
from end2endtest.helpers.Procedures import Procedures

class ComplexProcedures(Procedures):
    def doPasswordResetWithNewPassword(self, password):
        self.goToLoginPage()
        emailAddress = TE.assurerUser.email  # @UndefinedVariable
        self.initiatePasswordReset(emailAddress)
        cred = Credential.getByUser(TE.assurerUser, "email_for_password_reset")
        passwordResetLink = TE.pwresetUrl + "?secret=" + cred.secret
        self.clickPasswordResetLink(password, passwordResetLink)

    def registerFreshUser(self):
        self.goToLoginPage()
        self.registerUser()
        self.closeMessage()
        self.waitForTraces(["myappsCallback"])

    def registerAndGiveHash(self):
        self.registerFreshUser()
        self.goToLoginPage()
        digest = self.createHash()
        self.changeMyHash(digest)
        return digest

