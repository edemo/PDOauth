from pdoauth.ReportedError import ReportedError
from pdoauth.CredentialManager import CredentialManager
from flask import json
from pdoauth.models.Credential import Credential

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
        raise ReportedError(["Inactive or disabled user"], status=403)

    def passwordLogin(self, form):
        cred = CredentialManager.getCredentialFromForm(form)
        if cred is None:
            raise ReportedError(["Bad username or password"], status=403)
        return self.finishLogin(cred)

    def checkIdAgainstFacebookMe(self, form):
        code = form.secret.data
        resp = self.facebookMe(code)
        if 200 != resp.status:
            raise ReportedError(["Cannot login to facebook"], 403)
        data = json.loads(resp.data)
        if data["id"] != form.identifier.data:
            raise ReportedError(["bad facebook id"], 403)

    def facebookLogin(self, form):
        self.checkIdAgainstFacebookMe(form)
        cred = Credential.get("facebook", form.identifier.data)
        if cred is None:
            raise ReportedError(["You have to register first"], 403)
        return self.finishLogin(cred)
