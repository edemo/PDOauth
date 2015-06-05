import urllib3
import flask
from flask.globals import session, request
from flask_login import login_user, current_user, logout_user
from pdoauth.Responses import Responses

class FlaskInterface(Responses):

    def getHeader(self, header):
        return request.headers.get(header)

    def getCurrentUser(self):
        return current_user

    def getEnvironmentVariable(self, variableName):
        return request.environ.get(variableName, None)

    def getRequestForm(self):
        return request.form

    def getRequestUrl(self):
        return request.url

    def LogOut(self):
        return logout_user()

    def getConfig(self, name):
        return self.app.config.get(name)

    def validate_on_submit(self,form):
        return form.validate_on_submit()

    def _facebookMe(self, code):
        args = {"access_token":code, 
            "format":"json", 
            "method":"get"}
        http = urllib3.PoolManager()
        resp = http.request('GET', "https://graph.facebook.com/v2.2/me", args)
        return resp

    def getSession(self):
        return session

    def loginUserInFramework(self, user):
        r = login_user(user)
        return r

    def make_response(self, ret, status):
        return flask.make_response(ret, status)
