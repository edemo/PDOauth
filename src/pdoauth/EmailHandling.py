#pylint: disable=no-member
import time
from flask_mail import Message
from smtplib import SMTPException
from pdoauth.ReportedError import ReportedError
from pdoauth.Messages import exceptionSendingEmail, badChangeEmailSecret,\
    emailChangeEmailSent, emailChanged, thereIsAlreadyAUserWithThatEmail,\
    emailChangeIsCancelled
from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance
from pdoauth.models import User
from enforce.decorators import runtime_validation

class EmailData(object):
    def __init__(self, name, secret, expiry, addfields):
        self.name = name
        self.secret = secret
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
        for key in addfields:
            setattr(self,key,addfields[key])
    
    
@runtime_validation
class EmailHandling(object):
    passwordResetCredentialType = 'email_for_password_reset'

    def sendEmail(self, user, secret, expiry, topic, rmuser = False, recipient=None, **addfields):
        if recipient is None:
            recipient=user.email
        emailData = EmailData(user.email, secret, expiry, addfields)
        bodyTextCfg = topic + '_EMAIL_BODY_TEXT'
        bodyHtmlCfg = topic + '_EMAIL_BODY_HTML'
        subjectCfg = topic + '_EMAIL_SUBJECT'
        text = self.getConfig(bodyTextCfg).format(emailData)
        html = self.getConfig(bodyHtmlCfg).format(emailData)
        msg = Message(recipients=[recipient],
            body=text,
            html=html,
            subject=self.getConfig(subjectCfg),
            sender=self.getConfig('SERVER_EMAIL_ADDRESS'))
        try:
            self.mail.send(msg)
        except SMTPException as e:
            if rmuser:
                user.rm()
            raise ReportedError("{0}: {1}".format(exceptionSendingEmail,e))  # @UndefinedVariable

    def sendPasswordVerificationEmail(self, user):
        credentialType = 'emailcheck'
        secret, expiry = CredentialManager.createTemporaryCredential(user, credentialType)
        self.sendEmail(user, secret, expiry, "PASSWORD_VERIFICATION", rmuser = True)

    def sendPasswordResetMail(self, user):
        secret, expiry = CredentialManager.createTemporaryCredential(
                            user,
                            self.passwordResetCredentialType,
                            expiry=CredentialManager.fourHoursInSeconds)
        self.sendEmail(user, secret, expiry, "PASSWORD_RESET")

    def sendDeregisterMail(self, user):
        secret, expiry = CredentialManager.createTemporaryCredential(user, 'deregister')
        self.sendEmail(user, secret, expiry, "DEREGISTRATION")

    def sendHashCollisionMail(self, user: User, assured: bool, inAssurance: bool) -> None:
        if assured:
            if inAssurance:
                tag = "HASHCOLLISION_INASSURANCE"
            else:
                tag = "HASHCOLLISION_ASSURED"
        else:
            tag = "HASHCOLLISION_UNASSURED"
        self.sendEmail(user, None, None, tag)

    def changeEmail(self, form):
        user = self.getCurrentUser()
        self.emailChangeInit(form.newemail.data,user)
        return self.simple_response(emailChangeEmailSent)

    def emailChangeInit(self, newEmailAddress, user):
        if User.getByEmail(newEmailAddress):
            raise ReportedError(thereIsAlreadyAUserWithThatEmail, 418)
        secret, expiry = CredentialManager.createTemporaryCredential(user, "changeemail",additionalInfo=newEmailAddress )
        self.sendEmail(user, secret, expiry, "CHANGE_EMAIL_OLD", newemail=newEmailAddress, oldemail=user.email )
        secret, expiry = CredentialManager.createTemporaryCredential(user, "changeemailandverify",additionalInfo=newEmailAddress )
        self.sendEmail(user, secret, expiry, "CHANGE_EMAIL_NEW", recipient=newEmailAddress, newemail=newEmailAddress, oldemail=user.email)
        Credential.deleteExpired("changeemail")
        Credential.deleteExpired("changeemailandverify")

    def updateEmailByCredential(self, cred, verify):
        oldemail=cred.user.email
        cred.user.email = cred.getAdditionalInfo()
        cred.user.save()
        for assurance in Assurance.listByUser(cred.user, 'emailverification'):
            assurance.rm()
        if verify:
            Assurance.new(cred.user, 'emailverification', cred.user)
        else:
            self.sendPasswordVerificationEmail(cred.user)
        self.sendEmail(cred.user, None, None, "CHANGE_EMAIL_DONE",oldemail=oldemail, newemail=cred.user.email)

    def confirmEmailChange(self,form):
        return self.confirmChangeEmail(form.confirm.data, form.secret.data)
        

    def removeTemporaryEmailCredentials(self, cred):
        user = cred.user
        Credential.getByUser(user, "changeemail").rm()
        Credential.getByUser(user, "changeemailandverify").rm()


    def findTemporaryEmailCredential(self, secret):
        cred = Credential.getBySecret("changeemail", secret)
        verify = False
        if cred is None:
            credverify = Credential.getBySecret("changeemailandverify", secret)
            if credverify is None:
                raise ReportedError(badChangeEmailSecret, 403)
            else:
                cred = credverify
                verify = True
        return cred, verify

    def confirmChangeEmail(self, confirm, secret):
        cred, verify = self.findTemporaryEmailCredential(secret)
        if confirm is True:
            self.updateEmailByCredential(cred, verify)
            resp = self.simple_response(emailChanged)
        else:
            resp = self.simple_response(emailChangeIsCancelled)            
        self.removeTemporaryEmailCredentials(cred)
        return resp
