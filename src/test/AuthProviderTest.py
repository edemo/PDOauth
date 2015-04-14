
import unittest
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db

class Test(unittest.TestCase):


    def setUp(self):
        self.ap = AuthProvider()
        self.session = db.session
        self.app = Application.new("test app 5", "secret5")
        self.session.add(self.app)
        self.session.commit()
        
    def tearDown(self):
        self.session.close()
        unittest.TestCase.tearDown(self)
        
    def testValidateClientIdNoneClientIsFalse(self):
        self.assertFalse(self.ap.validate_client_id(None))

    def testValidateClientIdEmptyClientIsFalse(self):
        self.assertFalse(self.ap.validate_client_id(""))

    def testValidateClientIdExistingClientIsTrue(self):
        self.assertTrue(self.ap.validate_client_id(self.app.id))
        
    def testValidateClientSecretNoneIsFalse(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.id, None))

    def testValidateClientSecretEmptyIsFalse(self):
        self.assertFalse(self.ap.validate_client_secret(self.app.id, ""))

    def testValidateClientSecretExistingIsTrue(self):
        self.assertTrue(self.ap.validate_client_secret(self.app.id, self.app.secret))


if __name__ == "__main__":
    unittest.main()