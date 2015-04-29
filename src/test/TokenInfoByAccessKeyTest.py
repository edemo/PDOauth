from twatson.unittest_annotations import Fixture, test
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
        
    @test
    def TokenInfo_can_be_retrieved_by_access_key(self):
        self.assertEquals(self.tiba,TokenInfoByAccessKey.find('access key'))
        self.assertEquals(self.keydata,TokenInfoByAccessKey.find('access key').tokeninfo)
        
    @test
    def find_returns_None_for_nonexisting_refresh_key(self):
        self.assertEquals(None, TokenInfoByAccessKey.find('nonexisting'))
        
    @test
    def access_key_expires_at_given_time(self):
        now = time.time()
        self.assertEquals(self.tiba, TokenInfoByAccessKey.find('access key', _called_at=now+19))
        self.assertEquals(None, TokenInfoByAccessKey.find('access key', _called_at=now+21))
        
    @test
    def there_should_not_be_two_records_with_same_access_key(self):
        self.assertRaises(Exception, TokenInfoByAccessKey.new,'access key', self.keydata, 20)
