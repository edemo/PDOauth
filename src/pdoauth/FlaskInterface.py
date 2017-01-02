import flask
from flask.globals import session, request
from flask_login import login_user, current_user, logout_user
from pdoauth.Responses import Responses
import urllib
from pdoauth.WebInterface import WebInterface
from pdoauth.models.User import UserOrAnonymous
from werkzeug.local import LocalProxy
from enforce.decorators import runtime_validation

@runtime_validation
class FlaskInterface(Responses):
    def getRequest(self):
        return request

    def getCurrentUser(self) -> UserOrAnonymous:
        if isinstance(current_user, LocalProxy):
            return current_user._get_current_object()
        return current_user

    def logOut(self):
        return logout_user()

    def getSession(self):
        return session

    def loginUserInFramework(self, user):
        return login_user(user)

    def make_response(self, ret, status):
        return flask.make_response(ret, status)

    def facebookMe(self, code):
        args = {"access_token":code, 
            "format":"json", 
            "method":"get"}
        baseUri = "https://graph.facebook.com/v2.2/me"
        uri = WebInterface.parametrizeUri(baseUri, args)
        resp = urllib.request.urlopen(uri).read()
        return resp
