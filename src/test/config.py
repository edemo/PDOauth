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
    SERVER_NAME = "localhost.local"
    SERVER_EMAIL_ADDRESS = "test@edemokraciagep.org"
    PASSWORD_RESET_FORM_URL="https://{0}/static/login.html".format(SERVER_NAME)
