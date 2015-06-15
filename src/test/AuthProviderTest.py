# -*- coding: UTF-8 -*-

from twatson.unittest_annotations import Fixture, test
from pdoauth.AuthProvider import AuthProvider, DiscardingNonexistingToken
from pdoauth.models.Application import Application
from pdoauth.app import db
from pdoauth.models.KeyData import KeyData
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from test.helpers.AuthenticatedSessionMixin import AuthenticatedSessionMixin
from test.helpers.RandomUtil import RandomUtil
from test.helpers.FakeInterFace import FakeInterface

class AuthProviderTest(Fixture, AuthenticatedSessionMixin, RandomUtil):

    def setUp(self):
        self.setupRandom()
        Application.query.delete()  # @UndefinedVariable
        KeyData.query.delete()  # @UndefinedVariable
        TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.ap = AuthProvider(FakeInterface)
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
    def discarding_nonexistent_refresh_token_is_an_error(self):
        self.assertRaises(DiscardingNonexistingToken,self.ap.discard_refresh_token,'client_id', 'nonexisting')

