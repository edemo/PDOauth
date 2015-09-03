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
            self.controller = WebInterface(FlaskInterface())
            with app.test_request_context(*args,**kwargs):
                func(self)
            self.controller = WebInterface(FakeInterface())
            self.controller.interface.set_request_context(*args,**kwargs)
            func(self)
        decorated.func_name = func.func_name
        test(decorated)
        return decorated
    return decorator

class WebInterfaceTests(PDUnitTest, UserUtil):

    @test
    def webInterface_initializes_with_the_given_interface(self):
        interface = WebInterface(FlaskInterface())
        self.assertEqual(interface.interface.__class__, FlaskInterface)
        interface = WebInterface(FakeInterface())
        self.assertEqual(interface.interface.__class__, FakeInterface)

    @testForBothInterfaces()
    def you_can_getSession(self):
        session = self.controller.getSession()
        session['foo'] = 'bar'
        self.assertEqual(session['foo'], 'bar')

    @testForBothInterfaces()
    def you_can_getRequest(self):
        request = self.controller.getRequest()
        self.assertEqual(request.url, 'http://localhost/')

    @testForBothInterfaces('/foo')
    def request_url_corresponds_to_the_real_request_url(self):
        request = self.controller.getRequest()
        self.assertEqual(request.url, 'http://localhost/foo')

    @testForBothInterfaces()
    def user_can_be_logged_in_with_loginInFramework_using_credential(self):
        cred = self.createUserWithCredentials()
        self.controller.loginInFramework(cred)
        self.assertEqual(cred.user, self.controller.getCurrentUser())

    @testForBothInterfaces()
    def logged_in_user_can_be_obtained_with_getCurrentUser(self):
        cred = self.createUserWithCredentials()
        self.controller.loginInFramework(cred)
        self.assertEqual(cred.user, self.controller.getCurrentUser())

    @testForBothInterfaces(data=dict(foo='foo'), method='POST')
    def postdata_can_be_put_into_request_context(self):
        request = self.controller.getRequest()
        self.assertEqual(request.form['foo'], 'foo')

    @testForBothInterfaces()
    def facebook_interface_gives_error_for_bad_code(self):
        self.controller.interface.accessToken = 'notjunk'
        resp = self.controller.facebookMe('junk')
        self.assertEquals(resp.status, 400)
        self.assertEquals(resp.data, '{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}')

    @test
    def fake_facebookMe_returns_okay_if_interface_access_token_equals_code(self):
        interface = WebInterface(FakeInterface())
        interface.interface.accessToken = '42'
        interface.interface.facebook_id = 'f4c3b00c'
        resp = interface.facebookMe('42')
        respAsJson = json.loads(resp.data)
        self.assertEqual(respAsJson['id'], 'f4c3b00c')
        self.assertEqual(resp.status_code, 200)

    @testForBothInterfaces()
    def loginInFramework_returns_true_for_active_user(self):
        cred = self.createUserWithCredentials()
        response = self.controller.loginInFramework(cred)
        self.assertEqual(True, response)

    @testForBothInterfaces()
    def response_cookie_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42')

    @testForBothInterfaces()
    def cookie_setting_sets_the_header(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42')
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['csrf'], '42')

    @testForBothInterfaces()
    def cookie_domain_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42', domain="foo.bar.com")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Domain'], 'foo.bar.com')

    @testForBothInterfaces()
    def cookie_path_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42', path="/foo")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Path'], '/foo')

    @test
    def returnUserAndLoginCookie_sets_csrf_cookie(self):
        cred = self.createLoggedInUser()
        resp = self.controller.returnUserAndLoginCookie(cred.user)
        cookieparts = self.getCookieParts(resp)
        self.assertTrue(cookieparts.has_key('csrf'))

    @testForBothInterfaces(headers=dict(Authorization='foo'))
    def headers_can_be_obtained_with_getHeader(self):
        self.assertEquals(self.controller.getHeader('Authorization'), 'foo')

    @testForBothInterfaces(data=dict(bar='foo'), method='POST')
    def form_can_be_obtained_with_getRequestForm(self):
        self.assertEquals(self.controller.getRequestForm()['bar'], 'foo')

    @testForBothInterfaces()
    def logOut_logs_out(self):
        self.createLoggedInUser()
        self.assertTrue(self.controller.getCurrentUser().is_authenticated())
        self.controller.logOut()
        self.assertFalse(self.controller.getCurrentUser().is_authenticated())
