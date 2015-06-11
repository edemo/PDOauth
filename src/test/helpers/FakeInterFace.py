from flask import json

class FakeRecord(object):
    def __init__(self, value):
        self.data = value

class FakeForm(object):

    def set(self, key, value):
        return setattr(self, key, FakeRecord(value))

    def __init__(self,theDict):
        for key, value in theDict.items():
            self.set(key, value)

class FakeRequest():
    def __init__(self):
        self.url=None

class FakeSession(dict):
    pass

class FakeResponse(object):  
    def __init__(self, message, status):
        self.response = message
        self.data = message
        self.status_code = status
        self.status = status

class FakeInterface(object):
    def __init__(self):
        self.request = FakeRequest()
        self.session = FakeSession()
    def set_request_context(self, url='/', data=None, method = 'GET'):
        self.request.url='http://localhost'+url
        self.request.form = data
        self.request.method = method

    def getRequest(self):
        return self.request

    def getSession(self):
        return self.session

    def loginUserInFramework(self, user):
        self.current_user = user
        return True
    
    def getCurrentUser(self):
        return self.current_user
    
    def make_response(self, message, status):
        return FakeResponse(message,status)
    
    def _facebookMe(self, code):
        if self.access_token == code:
            return FakeResponse(json.dumps(dict(id=self.facebook_id)), 200)
        return FakeResponse('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}', 400)