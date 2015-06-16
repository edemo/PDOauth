#pylint: disable=star-args, unused-argument
from pdoauth.app import app
from test.helpers.UserUtil import UserUtil
from pdoauth.WebInterface import WebInterface
from test.helpers.FakeInterFace import FakeInterface
from pdoauth.FlaskInterface import FlaskInterface
from flask import json
from test.helpers.PDUnitTest import PDUnitTest, test

def testForBothInterfaces(*args,**kwargs):
    def decorator(func):
        def decorated(self):
            interface = WebInterface(FlaskInterface)
            with app.test_request_context(*args,**kwargs):
                func(self, interface)
            fakeInterface = WebInterface(FakeInterface)
            fakeInterface.interface.set_request_context(*args,**kwargs)
            func(self, fakeInterface)
        decorated.func_name = func.func_name
        test(decorated)
        return decorated
    return decorator

class WebInterfaceTests(PDUnitTest, UserUtil):

    @test
    def webInterface_initializes_with_the_given_interface(self):
        interface = WebInterface(FlaskInterface)
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
    def user_can_be_logged_in_with_loginInFramework_using_credential(self, interface):
        cred = self.createUserWithCredentials()
        interface.loginInFramework(cred)

    @testForBothInterfaces()
    def logged_in_user_can_be_obtained_with_getCurrentUser(self, interface):
        cred = self.createUserWithCredentials()
        interface.loginInFramework(cred)
        self.assertEqual(cred.user, interface.getCurrentUser())

    @testForBothInterfaces(data=dict(foo='foo'), method='POST')
    def postdata_can_be_put_into_request_context(self, interface):
        request = interface.getRequest()
        self.assertEqual(request.form['foo'], 'foo')

    @testForBothInterfaces()
    def facebook_interface_gives_error_for_bad_code(self, interface):
        interface.interface.accessToken = 'notjunk'
        resp = interface.facebookMe('junk')
        self.assertEquals(resp.status, 400)
        self.assertEquals(resp.data, '{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}')

    @test
    def fake_facebookMe_returns_okay_if_interface_access_token_equals_code(self):
        interface = WebInterface(FakeInterface)
        interface.interface.accessToken = '42'
        interface.interface.facebook_id = 'f4c3b00c'
        resp = interface.facebookMe('42')
        respAsJson = json.loads(resp.data)
        self.assertEqual(respAsJson['id'], 'f4c3b00c')
        self.assertEqual(resp.status_code, 200)

    @testForBothInterfaces()
    def loginInFramework_returns_true_for_active_user(self, interface):
        cred = self.createUserWithCredentials()
        response = interface.loginInFramework(cred)
        self.assertEqual(True, response)

    @testForBothInterfaces()
    def response_cookie_can_be_set(self, interface):
        response = interface.make_response("foo", 400)
        response.set_cookie('csrf', '42')

    @testForBothInterfaces()
    def cookie_setting_sets_the_header(self, interface):
        response = interface.make_response("foo", 400)
        response.set_cookie('csrf', '42')
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['csrf'], '42')

    @testForBothInterfaces()
    def cookie_domain_can_be_set(self, interface):
        response = interface.make_response("foo", 400)
        response.set_cookie('csrf', '42', domain="foo.bar.com")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Domain'], 'foo.bar.com')

    @testForBothInterfaces()
    def cookie_path_can_be_set(self, interface):
        response = interface.make_response("foo", 400)
        response.set_cookie('csrf', '42', path="/foo")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Path'], '/foo')

    @testForBothInterfaces()
    def returnUserAndLoginCookie_sets_csrf_cookie(self, interface):
        cred = self.createLoggedInUser()
        resp = self.controller.returnUserAndLoginCookie(cred.user)
        cookieparts = self.getCookieParts(resp)
        self.assertTrue(cookieparts.has_key('csrf'))
