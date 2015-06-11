from pdoauth.FlaskInterface import FlaskInterface
class Dummy(object):
    pass
class WebInterface(FlaskInterface, Dummy):
    
    def __init__(self, interfaceClass=None):
        if interfaceClass is None:
            interfaceClass = FlaskInterface
        self.setInterface(interfaceClass)

    def setInterface(self, interfaceClass):
        self.interface = interfaceClass()


    def getRequest(self):
        return self.interface.getRequest()

    def getHeader(self, header):
        return self.getRequest().headers.get(header)

    def getCurrentUser(self):
        return self.interface.getCurrentUser()

    def getEnvironmentVariable(self, variableName):
        return self.getRequest().environ.get(variableName, None)

    def getRequestForm(self):
        return self.getRequest().form

    def getRequestUrl(self):
        return self.getRequest().url

    def LogOut(self):
        return self.interface.LogOut()

    def getConfig(self, name):
        return self.app.config.get(name)

    def validate_on_submit(self,form):
        return form.validate_on_submit()

    def _facebookMe(self, code):
        return self.interface._facebookMe(code)

    def getSession(self):
        return self.interface.getSession()

    def loginUserInFramework(self, user):
        user.set_authenticated()
        return self.interface.loginUserInFramework(user)

    def make_response(self, ret, status):
        return self.interface.make_response(ret, status)
