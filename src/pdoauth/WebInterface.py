#pylint: disable=no-member
from uuid import uuid4
import uritools
from pdoauth.models.User import UserOrAnonymous
from enforce.decorators import runtime_validation

@runtime_validation
class WebInterface(object):

    def __init__(self, interfaceInstance):
        self.setInterface(interfaceInstance)

    @staticmethod
    def parametrizeUri(baseUri, params):
        parts = uritools.urisplit(baseUri)
        uri = uritools.uricompose(parts.scheme, parts.host, parts.path, params, port=parts.port)
        return uri

    def setInterface(self, interfaceInstance):
        self.interface = interfaceInstance

    def getRequest(self):
        return self.interface.getRequest()

    def getHeader(self, header):
        return self.getRequest().headers.get(header)

    def getCurrentUser(self) -> UserOrAnonymous:
        return self.interface.getCurrentUser()

    def getEnvironmentVariable(self, variableName):
        return self.getRequest().environ.get(variableName, None)

    def getRequestForm(self):
        return self.getRequest().form

    def getRequestUrl(self):
        request = self.getRequest()
        return request.url

    def logOut(self):
        return self.interface.logOut()

    def getConfig(self, name):
        return self.app.config.get(name)

    def facebookMe(self, code):
        return self.interface.facebookMe(code)

    def getSession(self):
        return self.interface.getSession()

    def getCSRF(self):
        return self.getSession()['csrf_token']

    def loginInFramework(self, credential):
        user = credential.user
        user.set_authenticated()
        token = uuid4().hex
        session = self.getSession()
        session['csrf_token'] = token
        session['login_credential'] = \
            (credential.credentialType, credential.identifier)
        return self.interface.loginUserInFramework(user)

    def makeRedirectResponse(self, redirectUri):
        response = self.make_response(redirectUri, 302)
        response.headers['Location']= redirectUri
        return response

    def make_response(self, ret, status):
        return self.interface.make_response(ret, status)
