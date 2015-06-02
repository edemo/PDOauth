from pdoauth.Controller import Controller
from flask import json
from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting
from pdoauth.models.Credential import Credential
from pdoauth.FlaskInterface import FlaskInterface
from pdoauth.ReportedError import ReportedError

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

class FacebookTest(Fixture, UserTesting):
    def setUp(self):
        Controller.unsetInterface(FlaskInterface)
        Controller.setInterface(FakeInterface)
        self.controller = Controller.getInstance()
        self.user = self.createUserWithCredentials(credType="facebook")
        self.user.activate()
        self.controller.facebook_id = self.usercreation_userid
        self.controller.access_token = self.usercreation_password
        data = {
                'credentialType': 'facebook',
                'identifier': self.controller.facebook_id,
                'secret': self.controller.access_token
        }
        self.request_data = FakeForm(data)

    def tearDown(self):
        Controller.unsetInterface(FakeInterface)        
        Controller.setInterface(FlaskInterface)        
    @test
    def facebook_login_needs_facebook_id_and_access_token(self):
        resp = self.controller.do_login(self.request_data)
        self.assertEqual(resp.status_code, 200)

    @test
    def facebook_login_needs_facebook_id_as_username(self):
        self.request_data.set('identifier','badid')
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
            self.assertEqual(e.status, 403)
            self.assertEqual(e.message,"bad facebook id")

    @test
    def facebook_login_needs_correct_access_token_as_password(self):
        self.request_data.set('secret',self.mkRandomPassword())
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
            self.assertEqual(e.status, 403)
            self.assertEqual(e.message, "Carnnot login to facebook")

    @test
    def facebook_login_needs_facebook_credentials_as_registered(self):
        cred = Credential.getByUser(self.user, "facebook")
        cred.rm()
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
            self.assertEqual(e.status, 403)
            self.assertEqual(e.message,"You have to register first")

    @test
    def facebookMe_reaches_facebook(self):
        Controller.unsetInterface(FakeInterface)
        Controller.setInterface(FlaskInterface)
        resp = self.controller._facebookMe("code")
        self.assertEqual(400, resp.status)
        self.assertTrue(resp.headers.has_key('x-fb-rev'))
        self.assertEqual('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}', resp.data)
        Controller.unsetInterface(FlaskInterface)
        Controller.setInterface(FakeInterface)
        