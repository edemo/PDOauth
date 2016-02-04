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
testSignatureAllOne = "73c6414bdcede8efd69706b6ada1196f837e79251d0a6a9d5b40461e53b98a8a7bdec785cd8d9cd20cf774f670741e684067aaa1c04a04710fa1e2eec712572b"
testSignatureAllTwo = "9a68d3fa324c080afd29b3b950ac82ee8ad1c7e0ca5d0b85f9b223d04756b91e291352c125a11d2e901f9350bc5aaf8d829536711b8c7b0f40e58d1314f48cbc"
skipSlowTests = False
skipFacebookTests = False
#fbuser does not allow email for the fb app, fbuesr2 does
fbuser = "mag+tesztelek@magwas.rulez.org"
fbpassword = "Elek the tester"
fbuserid = "111507052513637"
fbuser2 = "mag+elekne@magwas.rulez.org"
fbpassword2 = "Elekne is tesztel"
ca_certs = "src/end2endtest/server.crt"
