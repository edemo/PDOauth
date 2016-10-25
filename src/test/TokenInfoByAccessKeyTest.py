from twatson.unittest_annotations import Fixture
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
import time
from pdoauth.models.KeyData import KeyData

class TokenInfoByAccessKeyTest(Fixture):

    def setUp(self):
        TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.TokenInfo_can_be_stored_by_access_key()

    def TokenInfo_can_be_stored_by_access_key(self):
        self.keydata = KeyData.new('client_id', 'user_id', 'access_key', 'refresh_key')
        self.tiba = TokenInfoByAccessKey.new('access key', self.keydata, 20)
        
    
    def test_TokenInfo_can_be_retrieved_by_access_key(self):
        self.assertEqual(self.tiba,TokenInfoByAccessKey.find('access key'))
        self.assertEqual(self.keydata,TokenInfoByAccessKey.find('access key').tokeninfo)
        
    
    def test_find_returns_None_for_nonexisting_refresh_key(self):
        self.assertEqual(None, TokenInfoByAccessKey.find('nonexisting'))
        
    
    def test_access_key_expires_at_given_time(self):
        now = time.time()
        self.assertEqual(self.tiba, TokenInfoByAccessKey.find('access key', _called_at=now+19))
        self.assertEqual(None, TokenInfoByAccessKey.find('access key', _called_at=now+21))
        
    
    def test_there_should_not_be_two_records_with_same_access_key(self):
        self.assertRaises(Exception, TokenInfoByAccessKey.new,'access key', self.keydata, 20)
