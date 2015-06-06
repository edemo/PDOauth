from uuid import uuid4
from pdoauth.ReportedError import ReportedError
from pdoauth.CredentialManager import CredentialManager
from flask import json
from pdoauth.models.Credential import Credential

class LoginHandling(object):

    def loginUser(self, user):
        user.set_authenticated()
        r = self.loginUserInFramework(user)
        return r

    def returnUserAndLoginCookie(self, user, additionalInfo=None):
        if additionalInfo is None:
            additionalInfo={}
        resp = self.as_dict(user, **additionalInfo)
        token = unicode(uuid4())
        self.getSession()['csrf_token'] = token
        resp.set_cookie("csrf", token)
        return resp

    def finishLogin(self, user):
        r = self.loginUser(user)
        if r:
            return self.returnUserAndLoginCookie(user)
        raise ReportedError(["Inactive or disabled user"], status=403)

    def passwordLogin(self, form):
        user = CredentialManager.validate_from_form(form)
        if user is None:
            raise ReportedError(["Bad username or password"], status=403)
        return self.finishLogin(user)

    def checkIdAgainstFacebookMe(self, form):
        code = form.secret.data
        resp = self._facebookMe(code)
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
        return self.finishLogin(cred.user)
