from flask import json
from pdoauth.FlaskInterface import FlaskInterface
class FakeField(object):
    def __init__(self,value):
        self.data = value
        
class FakeForm(object):
    def __init__(self, theDict):
        for key, value in theDict.items():
            self.set(key, value)

    def set(self, key, value):
        field = FakeField(value)
        setattr(self, key, field)

class FakeResponse(object):
    def __init__(self,status,message):
        self.status_code = status
        self.status = status
        self.data = message
        self.response = [message]
        self.cookies = {}
        self.headers = {}
    
    def set_cookie(self,name,value):
        self.cookies[name] = value

class TestData(object):
    def __init__(self):
        self.headers = dict()
        self.request_url = ""
        self.environ = dict()

class FakeInterface(FlaskInterface):
    _testdata = TestData()
    
    def getHeader(self, header):
        return self._testdata.headers.get(header)

    def getCurrentUser(self):
        user = self._testdata.current_user
        return user

    def getEnvironmentVariable(self, variableName):
        return self._testdata.environ.get(variableName, None)

    def getRequestUrl(self):
        return self._testdata.request_url
    
    def __init__(self):
        self.headers = dict()

    def getRequestHeader(self, header):
        return self.headers.get(header)

    def validate_on_submit(self,form):
        for k in self.request_data.keys():
            getattr(form,k).data = self.request_data[k]
        return form.validate()

    def _facebookMe(self, code):
        if self.access_token == code:
            return FakeResponse(200, json.dumps(dict(id=self.facebook_id)))
        else:
            return FakeResponse(404,"fooo")
    
    def getSession(self):
        session = getattr(self, 'session', None)
        if session is None:
            session = dict()
            self.session = session
        return self.session

    def loginUserInFramework(self, user):
        self._testdata.current_user = user
        return user

    def make_response(self, ret, status):
        r = FakeResponse(status, ret)
        return r

class FakeMailer(object):

    def __init__(self):
        self.messages = list()

    def send_message(self, **kwargs):
        self.messages.append(kwargs)