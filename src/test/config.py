
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'test secret'
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/pdoauth.db"
    AUTHCODE_EXPIRY = 60