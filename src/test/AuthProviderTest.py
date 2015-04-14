'''
Created on Apr 13, 2015

@author: mag
'''
import unittest
from pdoauth.AuthProvider import AuthProvider

class Test(unittest.TestCase):


    def setUp(self):
        self.ap = AuthProvider()


    def tearDown(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()