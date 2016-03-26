#pylint: disable=no-member
import time
from flask_mail import Message
from smtplib import SMTPException
from pdoauth.ReportedError import ReportedError
from pdoauth.Messages import exceptionSendingEmail
from pdoauth.CredentialManager import CredentialManager

class EmailData(object):
    def __init__(self, name, secret, expiry):
        self.name = name
        self.secret = secret
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
    
    
class EmailHandling(object):
    passwordResetCredentialType = 'email_for_password_reset'

    def sendEmail(self, user, secret, expiry, topic, rmuser = False):
        emailData = EmailData(user.email, secret, expiry)
        bodyTextCfg = topic + '_EMAIL_BODY_TEXT'
        bodyHtmlCfg = topic + '_EMAIL_BODY_HTML'
        subjectCfg = topic + '_EMAIL_SUBJECT'
        text = self.getConfig(bodyTextCfg).format(emailData)
        html = self.getConfig(bodyHtmlCfg).format(emailData)
        msg = Message(recipients=[user.email],
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
