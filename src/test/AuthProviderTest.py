
from twatson.unittest_annotations import Fixture, test
from pdoauth.AuthProvider import AuthProvider, DiscardingNonexistingToken
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from flask.globals import session
from pdoauth.models.KeyData import KeyData

class FakeData(object):
    
    def __init__(self, client_id, user_id):
        self.client_id = client_id
        self.user_id = user_id


class FakeUser(object):
    def __init__(self):
        self.id = 'fakeuserid'


class AuthProviderTest(Fixture):

    def setUp(self):
        Application.query.delete()  # @UndefinedVariable
        KeyData.query.delete()  # @UndefinedVariable
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
        self.assertTrue(self.ap.validate_client_id(self.app.id))
        
    @test
    def validate_client_secret_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.id, None))

    @test
    def validate_client_secret_returns_False_for_empty_string(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.id, ""))

    @test
    def validate_client_secret_returns_False_for_wrong_secret(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.id, "different"))
        
    @test
    def validate_client_secret_returns_False_for_None_id(self):
        self.assertFalse(self.ap.validate_client_secret(None, None))
        
    @test
    def validate_client_secret_returns_True_for_good_secret(self):
        self.assertTrue(self.ap.validate_client_secret(self.app.id, self.app.secret))

    @test
    def validate_redirect_uri_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.id, None))

    @test
    def validate_redirect_uri_returns_False_for_bad_app(self):
        self.assertFalse(self.ap.validate_redirect_uri('some crap', "https://test.app/redirecturi"))
        
    @test
    def validate_redirect_uri_returns_False_for_empty(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.id, ""))

    @test
    def validate_redirect_uri_returns_False_for_wrong_uri(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.id, "some crap"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri(self):
        self.assertTrue(self.ap.validate_redirect_uri(self.app.id, "https://test.app/redirecturi"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri_with_parameters(self):
        self.assertTrue(self.ap.validate_redirect_uri(self.app.id, "https://test.app/redirecturi?param=value"))

    @test
    def validate_scope_returns_True_for_empty(self):
        self.assertTrue(self.ap.validate_scope(self.app.id, ""))
        
    @test
    def validate_scope_returns_False_for_nonempty(self):
        self.assertFalse(self.ap.validate_scope(self.app.id, "crap"))

    @test
    def validate_scope_returns_False_for_None(self):
        self.assertFalse(self.ap.validate_scope(self.app.id, "crap"))

    @test
    def validate_access_works_only_if_user_have_logged_in(self):
        with app.test_request_context('/'):
            session.user="pali"
            self.assertTrue(self.ap.validate_access())

    @test
    def validate_access_false_with_no_login(self):
        with app.test_request_context('/'):
            self.assertFalse(self.ap.validate_access())

    @test
    def validate_access_false_with_null_user(self):
        with app.test_request_context('/'):
            session.user=None
            self.assertFalse(self.ap.validate_access())

    def token_information_can_be_persisted(self):
        "with client_id, scope, access_token, token_type, expiry, refresh_token and_data"
        with app.test_request_context('/'):
            session.user = FakeUser()
            self.data = FakeData(client_id='client_id',user_id=session.user.id)
            self.ap.persist_token_information(self.data.client_id, '', 'access_token', 'token_type', 40, 'refresh_token', self.data)

    @test
    def data_can_be_retrieved_from_client_id__refresh_token_and_scope(self):
        self.token_information_can_be_persisted()
        retrievedData = self.ap.from_refresh_token(self.data.client_id, 'refresh_token', '')
        self.assertEquals(retrievedData.user_id, self.data.user_id)
        self.assertEquals(retrievedData.client_id, self.data.client_id)
    
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
            session.user = FakeUser()
            self.ap.persist_authorization_code('client_id', 'code', '')
    
    @test
    def key_data_can_be_retrieved_by_authorization_code(self):
        with app.test_request_context('/'):
            session.user = FakeUser()
            self.ap.persist_authorization_code('client_id', 'code', '')
        keyData = self.ap.from_authorization_code('client_id', 'code', '')
        self.assertEquals(keyData.user_id, 'fakeuserid')
        
    @test
    def authorization_code_can_be_obtained_with_client_id__secret_and_uri(self):
        with app.test_request_context('/'):
            session.user = FakeUser()
            redirectUri = 'https://test.app/redirecturi'
            resp = self.ap.get_authorization_code('code',
                               self.app.id,
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
                               self.app.id,
                               redirectUri, scope='')
        self.assertTrue(resp.headers['Location'].startswith('https://test.app/redirecturi?error=access_denied'))
