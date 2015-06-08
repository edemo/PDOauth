# -*- coding: UTF-8 -*-

from twatson.unittest_annotations import Fixture, test
from pdoauth.AuthProvider import AuthProvider, DiscardingNonexistingToken,\
    ScopeMustBeEmpty
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from pdoauth.models.KeyData import KeyData
from pyoauth2_shift.provider import utils
from flask_login import current_user
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from urllib import urlencode
from test.helpers.AuthenticatedSessionMixin import AuthenticatedSessionMixin
from test.helpers.RandomUtil import RandomUtil
from pdoauth import main  # @UnusedImport

class FakeData(object):
    
    def __init__(self, client_id, user_id):
        self.client_id = client_id
        self.user_id = user_id

class AuthProviderTest(Fixture, AuthenticatedSessionMixin, RandomUtil):

    def setUp(self):
        self.setupRandom()
        Application.query.delete()  # @UndefinedVariable
        KeyData.query.delete()  # @UndefinedVariable
        TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.ap = AuthProvider()
        self.session = db.session
        self.app = Application.new("test app 5", "secret5", "https://test.app/redirecturi")
        self.session.add(self.app)
        self.session.commit()
        
    def tearDown(self):
        self.session.close()
        
    @test
    def validate_client_id_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_client_id(None))

    @test
    def validate_client_id_returns_False_for_empty_string(self):
        self.assertFalse(self.ap.validate_client_id(""))

    @test
    def validate_client_id_returns_False_for_wrong_id(self):
        self.assertFalse(self.ap.validate_client_id("different"))
        
    @test
    def validate_client_id_returns_True_for_good_id(self):
        self.assertTrue(self.ap.validate_client_id(self.app.appid))
        
    @test
    def validate_client_secret_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.appid, None))

    @test
    def validate_client_secret_returns_False_for_empty_string(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.appid, ""))

    @test
    def validate_client_secret_returns_False_for_wrong_secret(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.appid, "different"))
        
    @test
    def validate_client_secret_returns_False_for_None_id(self):
        self.assertFalse(self.ap.validate_client_secret(None, None))
        
    @test
    def validate_client_secret_returns_True_for_good_secret(self):
        self.assertTrue(self.ap.validate_client_secret(self.app.appid, self.app.secret))

    @test
    def validate_redirect_uri_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.appid, None))

    @test
    def validate_redirect_uri_returns_False_for_bad_app(self):
        self.assertFalse(self.ap.validate_redirect_uri('some crap', "https://test.app/redirecturi"))
        
    @test
    def validate_redirect_uri_returns_False_for_empty(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.appid, ""))

    @test
    def validate_redirect_uri_returns_False_for_wrong_uri(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.appid, "some crap"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri(self):
        self.assertTrue(self.ap.validate_redirect_uri(self.app.appid, "https://test.app/redirecturi"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri_with_parameters(self):
        self.assertTrue(self.ap.validate_redirect_uri(self.app.appid, "https://test.app/redirecturi?param=value"))

    @test
    def validate_scope_returns_True_for_empty(self):
        self.assertTrue(self.ap.validate_scope(self.app.appid, ""))
        
    @test
    def validate_scope_returns_False_for_nonempty(self):
        self.assertFalse(self.ap.validate_scope(self.app.appid, "crap"))

    @test
    def validate_scope_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_scope(self.app.appid, "crap"))

    @test
    def validate_access_works_only_if_user_have_logged_in(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.assertTrue(self.ap.validate_access())

    @test
    def validate_access_false_with_no_login(self):
        with app.test_request_context('/'):
            self.assertFalse(self.ap.validate_access())

    def token_information_can_be_persisted(self):
        "with client_id, scope, access_token, token_type, expiry, refresh_token and_data"
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.data = FakeData(client_id='client_id',user_id=current_user.userid)
            self.ap.persist_token_information(self.data.client_id, '', 'access_token', 'token_type', 40, 'refresh_token', self.data)

    @test
    def data_can_be_retrieved_from_client_id__refresh_token_and_scope(self):
        self.token_information_can_be_persisted()
        retrievedData = self.ap.from_refresh_token(self.data.client_id, 'refresh_token', '')
        self.assertEquals(retrievedData.user_id, self.data.user_id)
        self.assertEquals(retrievedData.client_id, self.data.client_id)

    @test
    def nonempty_scope_is_an_error(self):
        self.token_information_can_be_persisted()
        self.assertRaises(ScopeMustBeEmpty, self.ap.from_refresh_token,self.data.client_id, 'refresh_token', 'nonempty')
    
    @test
    def refresh_token_can_be_discarded(self):
        self.token_information_can_be_persisted()
        self.ap.discard_refresh_token('client_id', 'refresh_token')
        self.assertEquals(None, self.ap.from_refresh_token(self.data.client_id, 'refresh_token', ''))
    
    @test
    def discarding_nonexistent_refresh_token_is_an_error(self):
        self.assertRaises(DiscardingNonexistingToken,self.ap.discard_refresh_token,'client_id', 'nonexisting')

    @test
    def authorization_code_can_be_persisted_with_key_data(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.ap.persist_authorization_code('client_id', 'code', '')
    
    @test
    def key_data_can_be_retrieved_by_authorization_code(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.ap.persist_authorization_code('client_id', 'code', '')
        keyData = self.ap.from_authorization_code('client_id', 'code', '')
        keyuserid = keyData.user_id
        myuserid = self.userid
        self.assertEquals(keyuserid, myuserid)
        
    @test
    def authorization_code_can_be_obtained_with_client_id__secret_and_uri(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            redirectUri = 'https://test.app/redirecturi'
            resp = self.ap.get_authorization_code('code',
                               self.app.appid,
                               redirectUri, scope='')
        self.assertEquals(302,resp.status_code)
        location = resp.headers['Location']
        self.assertTrue(location.startswith(redirectUri))
        self.assertTrue('&code=' in location)

    @test
    def authorization_code_cannot_be_obtained_without_user(self):
        with app.test_request_context('/'):
            redirectUri = 'https://test.app/redirecturi'
            resp = self.ap.get_authorization_code('code',
                               self.app.appid,
                               redirectUri, scope='')
        self.assertTrue(resp.headers['Location'].startswith('https://test.app/redirecturi?error=access_denied'))

    def getAuthorizationCode(self):
        with app.test_request_context('/'):
            redirect_uri = 'https://test.app/redirecturi'
            uri = 'https://localhost.local/v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri={1}'.format(self.app.appid, 
                redirect_uri)
            self.makeSessionAuthenticated()
            self.assertTrue(current_user.is_authenticated())
            params = utils.url_query_params(uri)
            self.assertEquals(self.app.appid, params['client_id'])
            self.assertTrue('response_type' in params)
            self.assertTrue('client_id' in params)
            self.assertTrue('redirect_uri' in params)
            self.assertEquals(params['response_type'], 'code')
            self.assertTrue(self.ap.validate_redirect_uri(params['client_id'], params['redirect_uri']))
            self.assertTrue(self.ap.validate_client_id(params['client_id']))
            self.assertTrue(self.ap.validate_access())
            self.ap.generate_authorization_code()
            resp = self.ap.get_authorization_code_from_uri(uri)
            self.assertEqual(302, resp.status_code)
            location = resp.headers['Location']
            self.assertTrue(location.startswith('https://test.app/redirecturi?code='))
            return location.split("=")[1]

    @test
    def authorization_code_can_be_obtained_from_uri(self):
        self.getAuthorizationCode()
            

    @test
    def authorization_code_can_be_discarded(self):
        appid = self.app.appid
        code = self.getAuthorizationCode()
        self.assertFalse(self.ap.from_authorization_code(appid, code, '') is None)
        self.ap.discard_authorization_code(appid, code)
        self.assertTrue(self.ap.from_authorization_code(appid, code, '') is None)
        
    @test
    def auth_interface_redirects_to_redirect_uri(self):
        params = {
            "response_type": "code",
            "client_id": self.app.name,
            "redirect_uri": self.app.redirect_uri
        }
        baseUrl = app.config.get('BASE_URL')
        uriBase = "/v1/oauth2/auth"
        queryString = urlencode(params)
        with app.test_client() as c:
            resp = c.get(uriBase, query_string=queryString, base_url=baseUrl)
            targetUri = "{0}?{1}".format(
                app.config.get('START_URL'),
                urlencode({"next": "{0}?{1}".format(baseUrl+uriBase, queryString)})
            )
        self.assertEquals(resp.status_code, 302)
        self.assertEquals(resp.headers['Location'],targetUri)
