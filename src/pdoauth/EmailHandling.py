#pylint: disable=no-member
from uuid import uuid4
import time
from pdoauth.models.Credential import Credential
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Message

class EmailData(object):
    def __init__(self, name, secret, expiry):
        self.name = name
        self.secret = secret
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
        self.expiry = time.strftime("%d %b %Y %H:%M:%S", time.gmtime(expiry))
    
    
class EmailHandling(object):
    passwordResetCredentialType = 'email_for_password_reset'

    def sendEmail(self, user, secret, expiry, topic):
        emailData = EmailData(user.email, secret, expiry)
        bodyTextCfg = topic + '_EMAIL_BODY_TEXT'
        bodyHtmlCfg = topic + '_EMAIL_BODY_HTML'
        subjectCfg = topic + '_EMAIL_SUBJECT'
        text = self.getConfig(bodyTextCfg).format(emailData)
        html = self.getConfig(bodyHtmlCfg).format(emailData)
        msg = Message(recipients=[user.email],
            body=text,
            subject=self.getConfig(subjectCfg),
            sender=self.getConfig('SERVER_EMAIL_ADDRESS'))
        msg.attach("email.html", "text/html", html)
        self.mail.send(msg)

    def sendPasswordVerificationEmail(self, user):
        secret=unicode(uuid4())
        expiry = time.time() + 60*60*24*4
        Credential.new(user, 'emailcheck', unicode(expiry), secret )
        self.sendEmail(user, secret, expiry, "PASSWORD_VERIFICATION")

    def sendPasswordResetMail(self, user):
        passwordResetEmailExpiration = 14400
        secret = unicode(uuid4())
        expirationTime = time.time() + passwordResetEmailExpiration
        expirationString = unicode(expirationTime)+":"+user.email
        Credential.new(user, self.passwordResetCredentialType, expirationString,secret)
        self.sendEmail(user, secret, expirationTime, "PASSWORD_RESET")

    def sendDeregisterMail(self, user):
        secret=unicode(uuid4())
        expiry = time.time() + 60*60*24*4
        Credential.new(user, 'deregister', unicode(expiry), secret )
        self.sendEmail(user, secret, expiry, "DEREGISTRATION")
