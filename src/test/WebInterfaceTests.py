from pdoauth.app import app
from test.helpers.UserUtil import UserUtil
from twatson.unittest_annotations import Fixture, test
from pdoauth.WebInterface import WebInterface
from test.helpers.FakeInterFace import FakeInterface
from pdoauth.FlaskInterface import FlaskInterface
from flask import json

def testForBothInterfaces(*args,**kwargs):
    def decorator(func):
        def f(self):
            interface = WebInterface()
            with app.test_request_context(*args,**kwargs):
                func(self, interface)
            fakeInterface = WebInterface(FakeInterface)
            fakeInterface.interface.set_request_context(*args,**kwargs)
            func(self, fakeInterface)
        f.func_name = func.func_name
        test(f)
        return f
    return decorator

class WebInterfaceTests(Fixture, UserUtil):

    @test
    def WebInterface_initializes_with_the_given_interface(self):
        interface = WebInterface()
        self.assertEqual(interface.interface.__class__, FlaskInterface)
        interface = WebInterface(FakeInterface)
        self.assertEqual(interface.interface.__class__, FakeInterface)
        
    @testForBothInterfaces()
    def you_can_getSession(self, interface):
            session = interface.getSession()
            session['foo'] = 'bar'
            self.assertEqual(session['foo'], 'bar')

    @testForBothInterfaces()
    def you_can_getRequest(self, interface):
        request = interface.getRequest()
        self.assertEqual(request.url, 'http://localhost/')

    @testForBothInterfaces('/foo')
    def request_url_corresponds_to_the_real_request_url(self, interface):
        request = interface.getRequest()
        self.assertEqual(request.url, 'http://localhost/foo')

    @testForBothInterfaces()
    def user_can_be_logged_in_with_loginUserInFramework(self, interface):
        #FIXME: should be done by credential
        user = self.createUserWithCredentials()
        interface.loginUserInFramework(user)

    @testForBothInterfaces()
    def logged_in_user_can_be_obtained_with_getCurrentUser(self, interface):
        user = self.createUserWithCredentials()
        interface.loginUserInFramework(user)
        self.assertEqual(user, interface.getCurrentUser())

    @testForBothInterfaces(data=dict(foo='foo'), method='POST')
    def postdata_can_be_put_into_request_context(self, interface):
        request = interface.getRequest()
        self.assertEqual(request.form['foo'], 'foo')
        
    @testForBothInterfaces()
    def facebook_interface_gives_error_for_bad_code(self, interface):
        interface.interface.access_token = 'notjunk'
        resp = interface._facebookMe('junk')
        self.assertEquals(resp.status, 400)
        self.assertEquals(resp.data, '{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}')

    @test
    def fake_facebookMe_returns_okay_if_interface_access_token_equals_code(self):
        interface = WebInterface(FakeInterface)
        interface.interface.access_token = '42'
        interface.interface.facebook_id = 'f4c3b00c'
        resp = interface._facebookMe('42')
        respAsJson = json.loads(resp.data)
        self.assertEqual(respAsJson['id'], 'f4c3b00c')
        self.assertEqual(resp.status_code, 200)

    @testForBothInterfaces()
    def loginUserInFramework_returns_true_for_active_user(self, interface):
        user = self.createUserWithCredentials()
        user.activate()
        r = interface.loginUserInFramework(user)
        self.assertEqual(True, r)
