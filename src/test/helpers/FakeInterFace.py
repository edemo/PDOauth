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
        self.cookies = {}
    
    def set_cookie(self,name,value):
        self.cookies[name] = value

class FakeInterface(FlaskInterface):

    def __init__(self):
        self.headers = dict()

    def getRequestHeader(self, header):
        return self.headers.get(header)

    def getCurrentUser(self):
        return self.current_user

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
        self.current_user = user
        return user

    def make_response(self, ret, status):
        r = FakeResponse(status, ret)
        return r
