# encoding: utf-8
import os
import tempfile

def absolutePathForEnd2EndResource(fileName):
    return os.path.join(os.path.dirname(__file__), "..", "end2endtest", fileName)

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    SECRET_KEY = 'test secret'
    SQLALCHEMY_DATABASE_URI = "postgres:///root"
    AUTHCODE_EXPIRY = 60
    WTF_CSRF_ENABLED = False
    MAIL_PORT = 1025
    SERVER_EMAIL_ADDRESS = "test@edemokraciagep.org"
    BASE_URL = "https://local.sso.edemokraciagep.org:8888"
    COOKIE_DOMAIN = "local.sso.edemokraciagep.org"
    SSL_LOGIN_BASE_URL = "https://local.sso.edemokraciagep.org:8889"
    SSL_LOGOUT_URL = "https://local.sso.edemokraciagep.org:8889/ssl_logout/"
    START_URL = "{0}/static/login.html".format(BASE_URL)
    PASSWORD_RESET_FORM_URL = START_URL
    FACEBOOK_APP_ID = "1632759003625536"
    FACEBOOK_APP_SECRET = "2698fa37973500db2ae740f6c0005601"
    CA_CERTIFICATE_FILE = absolutePathForEnd2EndResource("server.crt")
    CA_KEY_FILE = absolutePathForEnd2EndResource("server.key")
    SERVICE_NAME = "eDemokrácia SSO"
    DEREGISTRATION_URL = START_URL
    EMAIL_DOMAIN = "local.sso.edemokraciagep.org"
#    ANCHOR_URL = "https://anchor.edemokraciagep.org/"
    ANCHOR_URL = "https://local.sso.edemokraciagep.org:8890/"

testSignature = "8800f4a1d480e920e681df9e6a8026f7418dfab6cac74d49c020468327b254d74fee5d7c52893a2bf73c3a48bafc0f34ddd4bae1fbe6aa37159838504fa441069a6b4cd8e8c6269dc099d43f63558831f26f65d1ced0ee11fd775efd9e1fc3f996b3c8584d2e081c0c321e86798f367c9691d88887264ec29a79229702687630"
testSignatureAllOne = "76b9a2e5ebd633e2441e8f06c1ccc9258b61d3081a68c464c13f9bbea1513a33642346545bd3bf377cc4d5e66dce13f944f8958ec34bba93647f2f2b293112ca"
testSignatureAllTwo = "05454844af12232128031c650b91512c39af40937067d46b2a7bf3230be808039925df4e47eb7cc7d8273b3a9ba6db946defa5a2e41fecad004113da01cd44c4"
skipSlowTests = False
skipFacebookTests = False
#fbuser does not allow email for the fb app, fbuesr2 does
fbuser = "mag+tesztelek@magwas.rulez.org"
fbpassword = "Elek the tester"
fbuserid = "111507052513637"
fbuser2 = "mag+elekne@magwas.rulez.org"
fbpassword2 = "Elekne is tesztel"
ca_certs = "src/end2endtest/server.crt"
