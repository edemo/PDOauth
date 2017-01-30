# encoding: utf-8
import os
import logging

def absolutePathForEnd2EndResource(fileName):
    return os.path.join(os.path.dirname(__file__), "..", "end2endtest", fileName)

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    LOGLEVEL = logging.DEBUG
    SECRET_KEY = 'test secret'
    SQLALCHEMY_DATABASE_URI = "postgres:///root"
    AUTHCODE_EXPIRY = 60
    WTF_CSRF_ENABLED = False
    MAIL_PORT = 1025
    MAIL_SERVER = "127.0.0.1"
    MAIL_DEBUG = True
    SERVER_EMAIL_ADDRESS = "test@edemokraciagep.org"
    BASE_URL = "https://local.sso.edemokraciagep.org:8888"
    BACKEND_PATH = "/ada"
    COOKIE_DOMAIN = "local.sso.edemokraciagep.org"
    SSL_LOGIN_BASE_URL = "https://local.sso.edemokraciagep.org:8889"
    SSL_LOGOUT_URL = "https://local.sso.edemokraciagep.org:8889/ssl_logout/"
    START_URL = "{0}/static/fiokom.html".format(BASE_URL)
    LOGIN_URL = "{0}/static/login.html".format(BASE_URL)
    PASSWORD_RESET_FORM_URL = START_URL
    FACEBOOK_APP_ID = "1632759003625536"
    FACEBOOK_APP_SECRET = "2698fa37973500db2ae740f6c0005601"
    CA_CERTIFICATE_FILE = absolutePathForEnd2EndResource("server.crt")
    CA_KEY_FILE = absolutePathForEnd2EndResource("server.key")
    SERVICE_NAME = "eDemokrácia SSO"
    DEREGISTRATION_URL = LOGIN_URL
    EMAIL_DOMAIN = "local.sso.edemokraciagep.org"
#    ANCHOR_URL = "https://anchor.edemokraciagep.org/"
    ANCHOR_URL = "https://local.sso.edemokraciagep.org:8890/"
    CHANGE_EMAIL_DONE_EMAIL_SUBJECT = "warnemail address change has been done"
    CHANGE_EMAIL_DONE_EMAIL_BODY_TEXT = "warnDear {0.name},{0.oldemail}, {0.newemail}"
    CHANGE_EMAIL_DONE_EMAIL_BODY_HTML = "warnhtml {0.name}, {0.oldemail}, {0.newemail}"
    CHANGE_EMAIL_OLD_EMAIL_SUBJECT = "oldemail address change has been requested"
    CHANGE_EMAIL_OLD_EMAIL_BODY_TEXT = "oldDear {0.name}, {0.secret}, {0.expiry}, {0.oldemail}, {0.newemail}"
    CHANGE_EMAIL_OLD_EMAIL_BODY_HTML = "oldhtml {0.name}, {0.secret}, {0.expiry}, {0.oldemail}, {0.newemail}"
    CHANGE_EMAIL_NEW_EMAIL_SUBJECT = "new email address change has been requested"
    CHANGE_EMAIL_NEW_EMAIL_BODY_TEXT = "newDear {0.name}, {0.secret}, {0.expiry}, {0.oldemail}, {0.newemail}"
    CHANGE_EMAIL_NEW_EMAIL_BODY_HTML = "newhtml {0.name}, {0.secret}, {0.expiry}, {0.oldemail}, {0.newemail}"
    PASSWORD_VERIFICATION_EMAIL_SUBJECT = "verification"
    PASSWORD_VERIFICATION_EMAIL_BODY_TEXT = """Dear {0.name},
This is a verification email.
Go to https://local.sso.edemokraciagep.org:8888/v1/verify_email/{0.secret}
you have to do it until {0.expiry}.

Sincerely,
The Test machine
"""
    PASSWORD_VERIFICATION_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
This is a verification email.<br/>
Click <a href="https://local.sso.edemokraciagep.org:8888/v1/verify_email/{0.secret}">here</a><br/>
you have to do it until {0.expiry}.<br/>
<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""
    PASSWORD_RESET_EMAIL_SUBJECT = "password reset"
    PASSWORD_RESET_EMAIL_BODY_TEXT = """Dear {0.name},
This is a reset email.
Go to https://local.sso.edemokraciagep.org:8888/static/login.html?section=pwreset&secret={0.secret}
you have to do it until {0.expiry}.

Sincerely,
The Test machine
"""
    PASSWORD_RESET_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
This is a reset email.<br/>
Click <a href="https://local.sso.edemokraciagep.org:8888/static/login.html?section=pwreset&secret={0.secret}">Click</a><br/>
you have to do it until {0.expiry}.<br/>
<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""

    DEREGISTRATION_EMAIL_SUBJECT = "deregistration email"
    DEREGISTRATION_EMAIL_BODY_TEXT = """Dear {0.name},
This is a deregistration email.
Go to https://local.sso.edemokraciagep.org:8888/static/deregistration.html?deregistration_secret={0.secret}
you have to do it until {0.expiry}.

Sincerely,
The Test machine
"""
    DEREGISTRATION_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
This is a deregistration email.<br/>
Click <a href="https://local.sso.edemokraciagep.org:8888/static/deregistration.html?deregistration_secret={0.secret}">here</a><br/>
you have to do it until {0.expiry}.<br/>
<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""

    HASHCOLLISION_UNASSURED_EMAIL_SUBJECT = "hash collision email (unassured)"
    HASHCOLLISION_UNASSURED_EMAIL_BODY_TEXT = """Dear {0.name},
Someone have tried to register with your hash with adatom (unassured).

Sincerely,
The Test machine
"""
    HASHCOLLISION_UNASSURED_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
Someone have tried to register with your hash with adatom.(unassured)<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""
    HASHCOLLISION_ASSURED_EMAIL_SUBJECT = "hash collision email (assured)"
    HASHCOLLISION_ASSURED_EMAIL_BODY_TEXT = """Dear {0.name},
Someone have tried to register with your hash with adatom (assured).

Sincerely,
The Test machine
"""
    HASHCOLLISION_ASSURED_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
Someone have tried to register with your hash with adatom (assured).<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""
    HASHCOLLISION_INASSURANCE_EMAIL_SUBJECT = "hash collision email (inassurance)"
    HASHCOLLISION_INASSURANCE_EMAIL_BODY_TEXT = """Dear {0.name},
Someone have tried to register with your hash with adatom (inassurance).

Sincerely,
The Test machine
"""
    HASHCOLLISION_INASSURANCE_EMAIL_BODY_HTML = """<html><head></head><body>
Dear {0.name},<br>
Someone have tried to register with your hash with adatom (inassurance).<br/>
Sincerely,<br/>
The Test machine
</body></html>
"""

testSignatureAllOne = "fd0afb360d2772e544a5d952c4b4d63f93bd2e1e3c9cbd316a7950afdf5be4f25cfdc63097023aa3ecd7062e28e367c7f197a2501ee9daa1755161e862b904f5"
testSignatureAllTwo = "72bd4a1260f51aa6172862c1431e5e2537bf2d65ed74b9b76e4410760901f87cf892bb2621fa4d5d08e85a641ee8bc1026de8660caa61f4f206cd898c7ec6ef6"
skipSlowTests = False
skipFacebookTests = True
#fbuser does not allow email for the fb app, fbuesr2 does
class FBUser(object):
    def __init__(self,email, password, userid):
        self.email = email
        self.password = password
        self.userid = userid

facebookUser1 = FBUser(
    "hrynmco_carrierosen_1473330015@tfbnw.net",
    #"mag+tesztelek@magwas.rulez.org",
    "Elek the tester",
    "110746159383451")
    #"111507052513637")
facebookUser2 = FBUser(
    "wvbhblz_wisemanman_1473330385@tfbnw.net",
    #"mag+elekne3@magwas.rulez.org",
    "Elekne is tesztel",
    None)
ca_certs = "src/end2endtest/server.crt"
