from flask import json
from test import config

class FakeMail(object):
    def __init__(self):
        self.outbox = list()
    def send_message(self, subject, body, recipients, sender):
        self.outbox.append(dict(subject=subject, body=body, recipients=recipients, sender=sender))
class FakeApp(object):
    def __init__(self):
        self.config = config.Config()
        def get(value):
            return getattr(self.config, value)
        self.config.get = get

class FakeRecord(object):
    def __init__(self, value):

class FakeApp(object):
    def __init__(self):
        self.config=Config

class FakeField(object):
    def __init__(self,value):
        self.data = value

class FakeForm(object):

    def set(self, key, value):
        return setattr(self, key, FakeRecord(value))

    def __init__(self,theDict):
        for key, value in theDict.items():
            self.set(key, value)

class FakeRequest():
    def __init__(self):
        self.url='http://localhost/'
        self.environ = dict()
        self.form = dict()
        self.method = 'GET'
        
    def setUrl(self, url):
        self.url = 'http://localhost'+url
    def getUrl(self):
        return self.url
    def setEnviron(self, environ):
        self.environ = environ
    def getEnviron(self):
        return self.environ
    def setForm(self, form):
        self.form = form
    
    def setMethod(self, method):
        self.method = method

class FakeSession(dict):
    pass

class FakeResponse(object):  
    def __init__(self, message, status):
        self.response = message
        self.data = message
        self.status_code = status
        self.status = status
        self.cookies = dict()
        self.headers = dict()
    
    def set_cookie(self,name,value):
        self.cookies[name] = value


class ContextUrlIsAlreadySet(object):
    pass


class FakeInterface(object):
    def __init__(self):
        self._request = FakeRequest()
        self._session = FakeSession()
        self.urlSet = False

    def setEnviron(self, environ):
        if environ is None:
            environ = dict()
        self._request.setEnviron(environ)

    def set_request_context(self, url=None, data=None, method = 'GET', environ = None):
        request = self.getRequest()
        if url is not None:
            if self.urlSet is False:
                request.setUrl(url)
                self.urlSet = True
            else:
                raise ContextUrlIsAlreadySet()
        self._request.setForm(data)
        self._request.setMethod(method)
        self.setEnviron(environ)

    def getRequest(self):
        return self._request

    def getSession(self):
        return self._session

    def loginUserInFramework(self, user):
        self.current_user = user
        return True

    def logOut(self):
        self.current_user = None

    def getConfig(self, name):
        return getattr(self.app.config,name)


    def getCurrentUser(self):
        return self.current_user
    
    def make_response(self, message, status):
        return FakeResponse(message,status)
    
    def _facebookMe(self, code):
        if self.access_token == code:
            return FakeResponse(json.dumps(dict(id=self.facebook_id)), 200)
        return FakeResponse('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}', 400)
