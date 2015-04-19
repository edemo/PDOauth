
from twatson.unittest_annotations import Fixture, test,  main
from pdoauth.models.Application import Application, NotUnique, NonHttpsRedirectUri
from pdoauth.app import db

class ApplicationTest(Fixture):

    def setUp(self):
        Application.query.delete()  # @UndefinedVariable
        self.app = Application.new("test app1", "secret1", "https://test.app/redirecturi1")
        
    @test
    def the_application_name_is_stored_as_given(self):
        self.assertEquals(self.app.name, "test app1")

    @test
    def an_application_can_be_stored_and_retrieved(self):
        session = db.session
        session.add(self.app)
        session.commit()
        b = Application.get(self.app.id)
        self.assertEquals(self.app.name,b.name)
        self.assertEquals(self.app.id,b.id)
        session.close()
       
    @test 
    def the_name_of_the_application_must_be_unique(self):
        self.assertRaises(NotUnique,Application.new,"test app1", "secret1","https://test.app/redirecturi1")

    @test 
    def the_name_of_the_application_must_be_unique_case_2(self):
        self.assertRaises(NotUnique,Application.new,"test app1", "secret2", "https://test.app/redirecturi2")

    @test
    def the_redirect_uri_is_stored_as_given(self):
        self.assertEquals(self.app.redirect_uri, "https://test.app/redirecturi1")

    @test
    def the_redirect_uri_must_be_https(self):
        self.assertRaises(NonHttpsRedirectUri,Application.new,"test app3", "secret3", "http://test.app/redirecturi1")
