import urllib3
import flask
from flask.globals import session, request
from flask_login import login_user, current_user, logout_user
from pdoauth.Responses import Responses

class FlaskInterface(Responses):
    def getRequest(self):
        return request

    def getCurrentUser(self):
        return current_user

    def LogOut(self):
        return logout_user()

    def getSession(self):
        return session

    def loginUserInFramework(self, user):
        return login_user(user)

    def make_response(self, ret, status):
        return flask.make_response(ret, status)

    def _facebookMe(self, code):
        args = {"access_token":code, 
            "format":"json", 
            "method":"get"}
        http = urllib3.PoolManager()
        resp = http.request('GET', "https://graph.facebook.com/v2.2/me", args)
        return resp
