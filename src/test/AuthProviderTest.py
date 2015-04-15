
from twatson.unittest_annotations import Fixture, test, main
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db

class Test(Fixture):


    def setUp(self):
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

if __name__ == "__main__":
    main()