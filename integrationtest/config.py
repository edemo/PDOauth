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
    SERVER_NAME="127.0.0.1:8888"

print "sqlite_uri={0}".format(Config.SQLALCHEMY_DATABASE_URI)