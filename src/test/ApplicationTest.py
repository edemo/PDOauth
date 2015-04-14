
import unittest
from pdoauth.models.Application import Application
from pdoauth.app import db

class ApplicationTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = Application.new("test app1", "secret1")

    def testApplicationIdIsString(self):
        self.assertEquals(self.app.id.__class__, unicode)

    def testApplicationIdLengthIsFourteen(self):
        self.assertEquals(len(self.app.id), 14)
        
    def testApplicationNameIsTheGivenOne(self):
        self.assertEquals(self.app.name, "test app1")

    def testCreateandGet(self):
        session = db.session
        session.add(self.app)
        session.commit()
        b = Application.find(self.app.id)
        self.assertEquals(self.app.name,b.name)
        self.assertEquals(self.app.id,b.id)
        session.close()
        
    def testAppNameIsUnique(self):
        session = db.session
        session.add(self.app)
        session.commit()
        session.add(self.app)
        session.commit()
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()