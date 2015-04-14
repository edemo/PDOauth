
import unittest
from pdoauth.models.Application import Application


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCreateNew(self):
        Application()

    def testFind(self):
        Application.query.all()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()