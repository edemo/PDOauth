from pdoauth.ReportedError import ReportedError
from pdoauth.CredentialManager import CredentialManager
from flask import json
from pdoauth.models.Credential import Credential
from pdoauth.Messages import inactiveOrDisabledUser, badUserNameOrPassword,\
    cannotLoginToFacebook, youHaveToRegisterFirst
import urllib

class LoginHandling(object):

    def loginUser(self, cred):
        r = self.loginInFramework(cred)
        return r

    def setCSRFCookie(self, resp):
        resp.set_cookie("csrf", self.getCSRF(), domain=self.getConfig('COOKIE_DOMAIN'))

    def returnUserAndLoginCookie(self, user, additionalInfo=None):
        if additionalInfo is None:
            additionalInfo={}
        resp = self.as_dict(user, **additionalInfo)
        self.setCSRFCookie(resp)
        return resp

    def finishLogin(self, cred):
        r = self.loginUser(cred)
        if r:
            return self.returnUserAndLoginCookie(cred.user)
        raise ReportedError([inactiveOrDisabledUser], status=403)

    def passwordLogin(self, form):
        cred = CredentialManager.getCredentialFromForm(form)
        if cred is None:
            raise ReportedError([badUserNameOrPassword], status=403)
        return self.finishLogin(cred)

    def checkIdAgainstFacebookMe(self, form):
        code = form.password.data
        try:
            resp = self.facebookMe(code)
        except urllib.error.HTTPError as err:
            raise ReportedError([cannotLoginToFacebook, err.read()], 403)
        data = json.loads(resp)
        if data["id"] != form.identifier.data:
            raise ReportedError(["bad facebook id"], 403)

    def facebookLogin(self, form):
        self.checkIdAgainstFacebookMe(form)
        cred = Credential.get("facebook", form.identifier.data)
        if cred is None:
            raise ReportedError([youHaveToRegisterFirst], 403)
        return self.finishLogin(cred)
