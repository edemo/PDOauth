#pylint: disable=no-member, invalid-name, too-many-arguments
from flask import json
from test import config
from flask_login import AnonymousUserMixin
import urllib
from _io import StringIO

class FakeMail(object):
    def __init__(self):
        self.outbox = list()
    def send_message(self, subject, body, recipients, sender):
        msg = dict(
            subject=subject, body=body, recipients=recipients, sender=sender)
        self.send(msg)

    def send(self, msg):
        self.outbox.append(msg)

class FakeApp(object):
    def __init__(self):
        self.config = config.Config()
        def get(value):
            return getattr(self.config, value)
        self.config.get = get

class FakeRecord(object):
    def __init__(self, value):
        self.data = value

class FakeForm(object):
    def __init__(self,theDict):
        self.vals = dict()
        for key, value in theDict.items():
            self.set(key, value)
    def set(self, key, value):
        record = FakeRecord(value)
        setattr(self,key,record)
        self.vals[key] = record

    def __repr__(self, *args, **kwargs):
        values = []
        for key, value in self.vals.items():
            values.append("{0}={1}".format(key,value.data))
        return "FakeForm({0})".format(",".join(values))

class FakeRequest(object):
    def __init__(self):
        self.url='http://localhost/'
        self.environ = dict()
        self.form = dict()
        self.method = 'GET'
        self.headers = dict()

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
        if type(message)== str:
            message = [bytes(message.encode('utf-8'))]
        self._response = message
        self.data = message
        self.status_code = status
        self.status = status
        self.cookies = dict()
        self.headers = dict()

    @property
    def response(self):
        return self._response

    def set_cookie(self,name,value,path="/", domain = None):
        domainpart = ""
        if domain is not None:
            domainpart = " Domain={0};".format(domain)
        header = "{0}={1}; {3}Path={2}".format(name,value, path, domainpart)
        self.headers['Set-Cookie']=header

class ContextUrlIsAlreadySet(Exception):
    pass


class FakeInterface(object):
    def __init__(self):
        self.request = FakeRequest()
        self.session = FakeSession()
        self.current_user = None
        self.urlSet = False
        self.logOut()

    def setEnviron(self, environ):
        if environ is None:
            environ = dict()
        self.request.setEnviron(environ)

    def setHeaders(self, headers):
        if headers is None:
            headers = dict()
        self.request.setHeaders(headers)

    def setheaders(self, headers):
        if headers is None:
            headers = dict()
        self.request.headers = headers

    def set_request_context(self, url=None, data=None, method='GET', environ=None, headers=None, newUri=False):
        if newUri:
            self.request = FakeRequest()
            self.urlSet = False
        request = self.getRequest()
        if url is not None:
            if self.urlSet is False:
                request.setUrl(url)
                self.urlSet = True
            else:
                raise ContextUrlIsAlreadySet()
        self.request.setForm(data)
        self.request.setMethod(method)
        self.setEnviron(environ)
        self.setheaders(headers)

    def getRequest(self):
        return self.request

    def getSession(self):
        return self.session

    def loginUserInFramework(self, user):
        active = user.is_active()
        if active:
            self.current_user = user
        return active

    def logOut(self):
        self.current_user = AnonymousUserMixin()

    def getConfig(self, name):
        return getattr(self.app.config,name)


    def getCurrentUser(self):
        return self.current_user

    def make_response(self, message, status):
        return FakeResponse(message,status)

    def facebookMe(self, code):
        if self.accessToken == code:
            data = dict(id=self.facebook_id)
            return bytes(json.dumps(data).encode('utf-8'))
        #pylint: disable=line-too-long
        msg = '{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}'
        raise urllib.error.HTTPError(
                code=400,
                msg=msg,
                hdrs=list(),
                url="https://graph.facebook.com/v2.2/me",
                fp=StringIO(msg))
