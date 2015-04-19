
from twatson.unittest_annotations import Fixture, test
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from flask.globals import session


class AuthProviderTest(Fixture):

    def setUp(self):
        Application.query.delete()  # @UndefinedVariable
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
    def validate_redirect_uri_returns_False_for_empty(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.id, ""))

    @test
    def validate_redirect_uri_returns_False_for_wrong_uri(self):
        self.assertFalse(self.ap.validate_redirect_uri(self.app.id, "some crap"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri(self):
        self.assertTrue(self.ap.validate_redirect_uri(self.app.id, "https://test.app/redirecturi"))

    @test
    def validate_redirect_uri_returns_True_for_good_uri_with_paraeters(self):
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
