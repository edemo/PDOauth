#pylint: disable=star-args, unused-argument
from pdoauth.app import app
from test.helpers.UserUtil import UserUtil
from pdoauth.WebInterface import WebInterface
from test.helpers.FakeInterFace import FakeInterface
from pdoauth.FlaskInterface import FlaskInterface
from flask import json
from test.helpers.PDUnitTest import PDUnitTest
import urllib

class WebInterfaceTests(PDUnitTest, UserUtil):

    def forBothInterfaces(self, func, *args,**kwargs):
        self.controller = WebInterface(FlaskInterface())
        with app.test_request_context(*args,**kwargs):
            func()
        self.controller = WebInterface(FakeInterface())
        self.controller.interface.set_request_context(*args,**kwargs)
        func()

    def test_webInterface_initializes_with_the_given_interface(self):
        interface = WebInterface(FlaskInterface())
        self.assertEqual(interface.interface.__class__, FlaskInterface)
        interface = WebInterface(FakeInterface())
        self.assertEqual(interface.interface.__class__, FakeInterface)

    def you_can_getSession(self):
        session = self.controller.getSession()
        session['foo'] = 'bar'
        self.assertEqual(session['foo'], 'bar')

    def you_can_getRequest(self):
        request = self.controller.getRequest()
        self.assertEqual(request.url, 'http://localhost/')

    def request_url_corresponds_to_the_real_request_url(self):
        request = self.controller.getRequest()
        self.assertEqual(request.url, 'http://localhost/foo')

    def user_can_be_logged_in_with_loginInFramework_using_credential(self):
        cred = self.createUserWithCredentials()
        self.controller.loginInFramework(cred)
        self.assertEqual(cred.user, self.controller.getCurrentUser())

    def logged_in_user_can_be_obtained_with_getCurrentUser(self):
        cred = self.createUserWithCredentials()
        self.controller.loginInFramework(cred)
        self.assertEqual(cred.user, self.controller.getCurrentUser())

    def postdata_can_be_put_into_request_context(self):
        request = self.controller.getRequest()
        self.assertEqual(request.form['foo'], 'foo')

    def facebook_interface_gives_error_for_bad_code(self):
        self.controller.interface.accessToken = 'notjunk'
        try:
            FlaskInterface().facebookMe("junk")
        except urllib.error.HTTPError as err:
            self.assertEqual(400, err.code)
            self.assertTrue('x-fb-rev' in err.headers)
            self.assertTrue('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190' in str(err.read()))

    def test_fake_facebookMe_returns_okay_if_interface_access_token_equals_code(self):
        interface = WebInterface(FakeInterface())
        interface.interface.accessToken = '42'
        interface.interface.facebook_id = 'f4c3b00c'
        resp = interface.facebookMe('42')
        respAsJson = json.loads(resp)
        self.assertEqual(respAsJson['id'], 'f4c3b00c')

    def loginInFramework_returns_true_for_active_user(self):
        cred = self.createUserWithCredentials()
        response = self.controller.loginInFramework(cred)
        self.assertEqual(True, response)

    def response_cookie_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42')

    def cookie_setting_sets_the_header(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42')
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['csrf'], '42')

    def cookie_domain_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42', domain="foo.bar.com")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Domain'], 'foo.bar.com')

    def cookie_path_can_be_set(self):
        response = self.controller.make_response("foo", 400)
        response.set_cookie('csrf', '42', path="/foo")
        cookieparts = self.getCookieParts(response)
        self.assertEqual(cookieparts['Path'], '/foo')

    def test_returnUserAndLoginCookie_sets_csrf_cookie(self):
        cred = self.createLoggedInUser()
        resp = self.controller.returnUserAndLoginCookie(cred.user)
        cookieparts = self.getCookieParts(resp)
        self.assertTrue('csrf' in cookieparts)

    def headers_can_be_obtained_with_getHeader(self):
        self.assertEqual(self.controller.getHeader('Authorization'), 'foo')

    def form_can_be_obtained_with_getRequestForm(self):
        self.assertEqual(self.controller.getRequestForm()['bar'], 'foo')

    def logOut_logs_out(self):
        self.createLoggedInUser()
        self.assertTrue(self.controller.getCurrentUser().is_authenticated)
        self.controller.logOut()
        self.assertFalse(self.controller.getCurrentUser().is_authenticated)

    def test_things_for_both(self):
        self.forBothInterfaces(self.you_can_getSession)
        self.forBothInterfaces(self.you_can_getRequest)
        self.forBothInterfaces(self.request_url_corresponds_to_the_real_request_url,'/foo')
        self.forBothInterfaces(self.user_can_be_logged_in_with_loginInFramework_using_credential)
        self.forBothInterfaces(self.logged_in_user_can_be_obtained_with_getCurrentUser)
        self.forBothInterfaces(self.postdata_can_be_put_into_request_context,data=dict(foo='foo'), method='POST')
        self.forBothInterfaces(self.facebook_interface_gives_error_for_bad_code)
        self.forBothInterfaces(self.loginInFramework_returns_true_for_active_user)
        self.forBothInterfaces(self.response_cookie_can_be_set)
        self.forBothInterfaces(self.cookie_setting_sets_the_header)
        self.forBothInterfaces(self.cookie_domain_can_be_set)
        self.forBothInterfaces(self.cookie_path_can_be_set)
        self.forBothInterfaces(self.headers_can_be_obtained_with_getHeader,headers=dict(Authorization='foo'))
        self.forBothInterfaces(self.form_can_be_obtained_with_getRequestForm,data=dict(bar='foo'), method='POST')
        self.forBothInterfaces(self.logOut_logs_out)
