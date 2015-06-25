# encoding: utf-8
import os
import tempfile

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    SECRET_KEY = 'test secret'
    SQLALCHEMY_DATABASE_URI = "sqlite:////{0}".format(os.path.abspath(os.path.join(tempfile.gettempdir(),'pdoauth.db')))
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
    CA_CERTIFICATE_FILE = os.path.join(os.path.dirname(__file__), "..", "end2endtest","server.crt")
    CA_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "end2endtest","server.key")
    SERVICE_NAME = "eDemokrácia SSO"
    DEREGISTRATION_URL = START_URL
    EMAIL_DOMAIN = "local.sso.edemokraciagep.org"

testSignature = "8800f4a1d480e920e681df9e6a8026f7418dfab6cac74d49c020468327b254d74fee5d7c52893a2bf73c3a48bafc0f34ddd4bae1fbe6aa37159838504fa441069a6b4cd8e8c6269dc099d43f63558831f26f65d1ced0ee11fd775efd9e1fc3f996b3c8584d2e081c0c321e86798f367c9691d88887264ec29a79229702687630"
testSignatureAllOne = "2658cad18da9bf60338e81f69f636740ecbc88115d004d4ba465aedd91a725b81316e99ba819426297f6ce93c13bbf7571431b751b9a0879895d36818b3725dd"
testSignatureAllTwo = "188c22c817b78882681287783c584a3b12fa137444dd1038d12cc37bcc8227c0d497f378662ec6803def36a2cbfa9fe94ea307eedd4a5791fce069505bb09c54"
skipSlowTests = True
skipFacebookTests = False
#fbuser does not allow email for the fb app, fbuesr2 does
fbuser = "mag+tesztelek@magwas.rulez.org"
fbpassword = "Elek the tester"
fbuserid = "111507052513637"
fbuser2 = "mag+elekne@magwas.rulez.org"
fbpassword2 = "Elekne is tesztel"
ca_certs = "src/end2endtest/server.crt"
