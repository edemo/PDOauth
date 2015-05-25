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
    SERVER_NAME = "local.sso.edemokraciagep.org:8888"
    BASE_URL = "http://" + SERVER_NAME
    SERVER_EMAIL_ADDRESS = "test@edemokraciagep.org"
    PASSWORD_RESET_FORM_URL="https://{0}/static/login.html".format(SERVER_NAME)
    FACEBOOK_APP_ID = "1632759003625536"
    FACEBOOK_APP_SECRET = "2698fa37973500db2ae740f6c0005601"
    CA_CERTIFICATE_FILE = os.path.join(os.path.dirname(__file__), "..", "integrationtest","server.crt")
    CA_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "integrationtest","server.key")

base_url = Config.BASE_URL
