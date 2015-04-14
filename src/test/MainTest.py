
import unittest

from pdoauth.app import app

class Test(unittest.TestCase):


    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def testNoRootUri(self):
        resp = self.app.get("/")
        self.assertEquals(resp.status_code, 404,)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()