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
    #SERVER_NAME="local.sso.edemokraciagep.org:8889"
    BASE_URL = "https://" + "local.sso.edemokraciagep.org:8888"
    SSL_LOGIN_URL = "https://" + "local.sso.edemokraciagep.org:8889/ssl_login"
    PASSWORD_RESET_FORM_URL="{0}/static/login.html".format(BASE_URL)
    FACEBOOK_APP_ID = "1632759003625536"
    FACEBOOK_APP_SECRET = "2698fa37973500db2ae740f6c0005601"

testSignature = "8800f4a1d480e920e681df9e6a8026f7418dfab6cac74d49c020468327b254d74fee5d7c52893a2bf73c3a48bafc0f34ddd4bae1fbe6aa37159838504fa441069a6b4cd8e8c6269dc099d43f63558831f26f65d1ced0ee11fd775efd9e1fc3f996b3c8584d2e081c0c321e86798f367c9691d88887264ec29a79229702687630"
testSignatureAllOne = "2658cad18da9bf60338e81f69f636740ecbc88115d004d4ba465aedd91a725b81316e99ba819426297f6ce93c13bbf7571431b751b9a0879895d36818b3725dd5dd34a689ff154046f3b12252c3241a45f740dd42351142ac02fd7d1aaaf76180f45176abb37a0e9f305e426f075cef09faaf4e55d6ba52eee7d77ef697ef4880e93c4096017db34a7cac309809f70f752a729d15333c1e128240fc698cb84dd90ee39ca7f1678acbbba409e83b2bb77db72b50b71d1149e01b15c3e23d391fed30bae3d0d19cd91545423dda879c9a4a6a7f18a4d8b80ee1964d9390bea7c7ac9996c83ca29baee03affe22a2c43fbf662e0d931073c8dc8225390e84156702"
testSignatureAllTwo = "188c22c817b78882681287783c584a3b12fa137444dd1038d12cc37bcc8227c0d497f378662ec6803def36a2cbfa9fe94ea307eedd4a5791fce069505bb09c534a67eb902fe4fe4be989e8f35542f11db3368606c5bf2307521319ead3a87c6cfda3d883bdce12895f8054d3d91e1435a87a41db589fedca14ccdbb2da6ab9d36f524dcac521530d2392efe04bcffc96021df18dca7444be401e812b97a1e4a42181b20fa62fb7eb49731ad0dc2a8ab5a287c318ca90e61c10946614e59743f52ee4b0a929f13bc41c35e89da12f635b3137acd13255ce394dfa8590f67efd0bc14147b190506ab884ecb158b5233b32c9495dbdfdb06b29fc748565b3ef707a"
skipSlowTests = True
skipFacebookTests = False
#fbuser does not allow email for the fb app, fbuesr2 does
fbuser = "mag+tesztelek@magwas.rulez.org"
fbpassword = "Elek the tester"
fbuserid = "111507052513637"
fbuser2 = "mag+elekne@magwas.rulez.org"
fbpassword2 = "Elekne is tesztel"
ca_certs = "src/integrationtest/server.crt"
