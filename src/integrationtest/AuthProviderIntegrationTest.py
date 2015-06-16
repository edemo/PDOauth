# -*- coding: UTF-8 -*-
# pylint: disable=no-member, invalid-name
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.AuthProvider import AuthProvider, ScopeMustBeEmpty
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from pdoauth.models.KeyData import KeyData
from pyoauth2_shift.provider import utils
from flask_login import current_user
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from urllib import urlencode
from test.helpers.AuthenticatedSessionMixin import AuthenticatedSessionMixin
from test.helpers.RandomUtil import RandomUtil
from pdoauth.FlaskInterface import FlaskInterface

class FakeData(object):

    def __init__(self, client_id, user_id):
        self.client_id = client_id
        self.user_id = user_id

class AuthProviderIntegrationTest(
        IntegrationTest, AuthenticatedSessionMixin, RandomUtil):

    def setUp(self):
        self.setupRandom()
        Application.query.delete()  # @UndefinedVariable
        KeyData.query.delete()  # @UndefinedVariable
        TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.authProvider = AuthProvider(FlaskInterface())
        self.session = db.session
        self.app = Application.new(
            "test app 5", "secret5", "https://test.app/redirecturi")
        self.session.add(self.app)
        self.session.commit()

    def tearDown(self):
        self.session.close()


    @test
    def validate_access_works_only_if_user_have_logged_in(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.assertTrue(self.authProvider.validate_access())

    @test
    def validate_access_false_with_no_login(self):
        with app.test_request_context('/'):
            self.assertFalse(self.authProvider.validate_access())

    def token_information_can_be_persisted(self):
        """With client_id, scope, access_token,
        token_type, expiry, refresh_token and_data"""
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            userid = current_user.userid
            self.data = FakeData(client_id='client_id',user_id=userid)
            self.authProvider.persist_token_information(
                self.data.client_id,
                '',
                'access_token',
                'token_type',
                40,
                'refresh_token',
                self.data)

    @test
    def data_can_be_retrieved_from_client_id__refresh_token_and_scope(self):
        self.token_information_can_be_persisted()
        retrievedData = self.authProvider.from_refresh_token(
                            self.data.client_id, 'refresh_token', '')
        self.assertEquals(retrievedData.user_id, self.data.user_id)
        self.assertEquals(retrievedData.client_id, self.data.client_id)

    @test
    def nonempty_scope_is_an_error(self):
        self.token_information_can_be_persisted()
        self.assertRaises(
            ScopeMustBeEmpty,
            self.authProvider.from_refresh_token,self.data.client_id,
            'refresh_token',
            'nonempty')

    @test
    def refresh_token_can_be_discarded(self):
        self.token_information_can_be_persisted()
        self.authProvider.discard_refresh_token('client_id', 'refresh_token')
        self.assertEquals(
            None,
            self.authProvider.from_refresh_token(
                self.data.client_id, 'refresh_token', ''))

    @test
    def authorization_code_can_be_persisted_with_key_data(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.authProvider.persist_authorization_code(
                'client_id', 'code', '')

    @test
    def key_data_can_be_retrieved_by_authorization_code(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            self.authProvider.persist_authorization_code(
                'client_id', 'code', '')
        keyData = self.authProvider.from_authorization_code(
                        'client_id', 'code', '')
        keyuserid = keyData.user_id
        myuserid = self.userid
        self.assertEquals(keyuserid, myuserid)

    @test
    def authorization_code_can_be_obtained_with_client_id__secret_and_uri(self):
        with app.test_request_context('/'):
            self.makeSessionAuthenticated()
            redirectUri = 'https://test.app/redirecturi'
            resp = self.authProvider.get_authorization_code('code',
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
            resp = self.authProvider.get_authorization_code('code',
                               self.app.appid,
                               redirectUri, scope='')
        uri = 'https://test.app/redirecturi?error=access_denied'
        self.assertTrue(
            resp.headers['Location'].startswith(uri))

    def _getAuthorizationCode(self):
        with app.test_request_context('/'):
            redirect_uri = 'https://test.app/redirecturi'
            uriPattern = 'https://localhost.local/v1/oauth2/auth?response_type=code&client_id={0}&redirect_uri={1}'
            uri = uriPattern.format(self.app.appid, redirect_uri)
            self.makeSessionAuthenticated()
            self.assertTrue(current_user.is_authenticated())
            params = utils.url_query_params(uri)
            self.assertEquals(self.app.appid, params['client_id'])
            self.assertTrue('response_type' in params)
            self.assertTrue('client_id' in params)
            self.assertTrue('redirect_uri' in params)
            self.assertEquals(params['response_type'], 'code')
            self.assertTrue(
                self.authProvider.validate_redirect_uri(
                    params['client_id'], params['redirect_uri']))
            self.assertTrue(
                self.authProvider.validate_client_id(params['client_id']))
            self.assertTrue(self.authProvider.validate_access())
            self.authProvider.generate_authorization_code()
            resp = self.authProvider.get_authorization_code_from_uri(uri)
            self.assertEqual(302, resp.status_code)
            location = resp.headers['Location']
            uriStart = 'https://test.app/redirecturi?code='
            self.assertTrue(location.startswith(uriStart))
            return location.split("=")[1]

    @test
    def authorization_code_can_be_obtained_from_uri(self):
        self._getAuthorizationCode()

    def isEmptyFromCde(self, appid, code):
        theCode = self.authProvider.from_authorization_code(appid, code, '')
        return theCode is None

    @test
    def authorization_code_can_be_discarded(self):
        appid = self.app.appid
        code = self._getAuthorizationCode()
        self.assertFalse(self.isEmptyFromCde(appid, code))
        self.authProvider.discard_authorization_code(appid, code)
        self.assertTrue(self.isEmptyFromCde(appid, code))

    @test
    def auth_interface_redirects_to_redirect_uri(self):
        params = {
            "response_type": "code",
            "client_id": self.app.name,
            "redirectUri": self.app.redirect_uri
        }
        baseUrl = app.config.get('BASE_URL')
        uriBase = "/v1/oauth2/auth"
        queryString = urlencode(params)
        with app.test_client() as client:
            resp = client.get(
                    uriBase, query_string=queryString, base_url=baseUrl)
            theUri = baseUrl + uriBase
            targetUri = "{0}?{1}".format(
                app.config.get('START_URL'),
                urlencode({"next": "{0}?{1}".format(theUri, queryString)})
            )
        self.assertEquals(resp.status_code, 302)
        self.assertEquals(resp.headers['Location'],targetUri)
