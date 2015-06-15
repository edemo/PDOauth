from uuid import uuid4
import time
from pdoauth.models.Credential import Credential
class EmailHandling(object):

    def sendPasswordVerificationEmail(self, user):
        secret=unicode(uuid4())
        expiry = time.time() + 60*60*24*4
        Credential.new(user, 'emailcheck', unicode(expiry), secret )
        timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
        uri = "{0}/v1/verify_email/{1}".format(self.getConfig('BASE_URL'),secret)
        text = """Hi, click on <a href="{0}">{0}</a> until {1} to verify your email""".format(uri, timeText)
        self.mail.send_message(subject="verification", body=text, recipients=[user.email], sender=self.getConfig('SERVER_EMAIL_ADDRESS'))
    
    def sendPasswordResetMail(self, user, secret, expiry):
        timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
        serverName = self.getConfig('SERVICE_NAME')
        uri = "{0}?secret={1}".format(self.getConfig("PASSWORD_RESET_FORM_URL"), secret, user.email)
        text = """Hi, click on <a href="{0}">{0}</a> until {1} to reset your password""".format(uri, timeText)
        subject = "Password Reset for {0}".format(serverName)
        self.mail.send_message(subject=subject, body=text, recipients=[user.email], sender=self.getConfig('SERVER_EMAIL_ADDRESS'))

    def sendDeregisterMail(self, user):
        secret=unicode(uuid4())
        expiry = time.time() + 60*60*24*4
        timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
        serverName = self.getConfig('SERVICE_NAME')
        Credential.new(user, 'deregister', unicode(expiry), secret )
        uri = "{0}?deregistration_secret={1}".format(self.getConfig("DEREGISTRATION_URL"), secret, user.email)
        text = """Hi, click on <a href="{0}">{0}</a> until {1} to deregister""".format(uri, timeText)
        subject = "Deregistration for {0}".format(serverName)
        self.mail.send_message(subject=subject, body=text, recipients=[user.email], sender=self.getConfig('SERVER_EMAIL_ADDRESS'))
