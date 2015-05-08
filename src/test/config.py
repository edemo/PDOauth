
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = False
    SECRET_KEY = 'test secret'
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/pdoauth.db"
    AUTHCODE_EXPIRY = 60
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost.local"
    SERVER_EMAIL_ADDRESS = "test@edemokraciagep.org"
