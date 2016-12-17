#pylint: disable=no-member
from pdoauth.models.Application import Application,\
    NotUnique, NonHttpsRedirectUri
from pdoauth.app import db
from pdoauth.models.AppAssurance import AppAssurance
from pdoauth.models.AppMap import AppMap
from unittest.case import TestCase

class ApplicationTest(TestCase):

    def setUp(self):
        AppMap.query.delete() #@UndefinedVariable
        AppAssurance.query.delete() #@UndefinedVariable
        Application.query.delete()  #@UndefinedVariable
        self.app = Application.new(
            "test app1", "secret1", "https://test.app/redirecturi1")

    
    def test_the_application_name_is_stored_as_given(self):
        self.assertEqual(self.app.name, "test app1")

    
    def test_an_application_can_be_stored_and_retrieved(self):
        session = db.session
        session.add(self.app)
        session.commit()
        application = Application.get(self.app.appid)
        self.assertEqual(self.app.name,application.name)
        self.assertEqual(self.app.appid,application.appid)
        session.close()

    
    def test_the_name_of_the_application_must_be_unique(self):
        self.assertRaises(
            NotUnique, Application.new, "test app1",
            "secret1","https://test.app/redirecturi1")

    
    def test_the_name_of_the_application_must_be_unique_case_2(self):
        self.assertRaises(
            NotUnique, Application.new, "test app1",
            "secret2", "https://test.app/redirecturi2")

    
    def test_the_redirect_uri_is_stored_as_given(self):
        self.assertEqual(
            self.app.redirect_uri, "https://test.app/redirecturi1")

    
    def test_the_redirect_uri_must_be_https(self):
        self.assertRaises(
            NonHttpsRedirectUri, Application.new,
            "test app3", "secret3", "http://test.app/redirecturi1")

    
    def test_by_default_the_application_cannot_email(self):
        self.assertEqual(False,self.app.can_email)
        
    
    def test_can_email_is_saved(self):
        self.app.can_email = True
        self.app.save()
        app = Application.get(self.app.appid)
        self.assertEqual(True, app.can_email)
