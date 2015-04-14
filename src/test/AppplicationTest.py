
import unittest
from pdoauth.models.Application import Application


class Test(unittest.TestCase):


    def testCreateNew(self):
        Application()

    def testFind(self):
        Application.query.all()  # @UndefinedVariable


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()