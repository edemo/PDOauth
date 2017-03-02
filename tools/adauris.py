import os
import json
from config import Config

data=json.dumps(dict(
    BASE_URL = Config.BASE_URL,
    BACKEND_PATH = Config.BACKEND_PATH,
    START_URL = Config.START_URL,
    LOGIN_URL = Config.LOGIN_URL,
    PASSWORD_RESET_FORM_URL = Config.PASSWORD_RESET_FORM_URL,
    SSL_LOGIN_BASE_URL = Config.SSL_LOGIN_BASE_URL,
    SSL_LOGOUT_URL = Config.SSL_LOGOUT_URL,
    ANCHOR_URL = Config.ANCHOR_URL,
    FACEBOOK_APP_ID = Config.FACEBOOK_APP_ID,
))

with open('./site/js/modules/adauris.js','w') as file:
	file.write( 'export var uris=%s' % data )