from twatson.unittest_annotations import Fixture, main, test
from pdoauth.models.TokenInfo import TokenInfo
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
import time

class TokenInfoByAccessKeyTest(Fixture):

    def setUp(self):
        TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.TokenInfo_can_be_stored_by_access_key()

    def TokenInfo_can_be_stored_by_access_key(self):
        self.tokeninfo = TokenInfo.new("refresh_key")
        self.tiba = TokenInfoByAccessKey.new('access key', self.tokeninfo, 20)
        
    @test
    def TokenInfo_can_be_retrieved_by_access_key(self):
        self.assertEquals(self.tiba,TokenInfoByAccessKey.getExisting('access key'))
        self.assertEquals(self.tokeninfo,TokenInfoByAccessKey.getExisting('access key').tokeninfo)
        
    @test
    def getExisting_returns_None_for_nonexisting_refresh_key(self):
        self.assertEquals(None, TokenInfoByAccessKey.getExisting('nonexisting'))
        
    @test
    def access_key_expires_at_given_time(self):
        now = time.time()
        self.assertEquals(self.tiba, TokenInfoByAccessKey.getExisting('access key', _called_at=now+19))
        self.assertEquals(None, TokenInfoByAccessKey.getExisting('access key', _called_at=now+21))
        
    @test
    def there_should_not_be_two_records_with_same_access_key(self):
        self.assertRaises(Exception, TokenInfoByAccessKey.new,'access key', self.tokeninfo, 20)

if __name__ == "__main__":
    main()