from twatson.unittest_annotations import Fixture, main, test
from pdoauth.models.TokenInfo import TokenInfo

class TokenInfoTest(Fixture):

    def setUp(self):
        self.tokeninfo = self.TokenInfo_can_be_created_with_refresh_key()
        
    def TokenInfo_can_be_created_with_refresh_key(self):
        return TokenInfo.new('refresh_key')

    @test
    def Created_TokenInfo_have_id(self):
        self.assertTrue(self.tokeninfo.id is not None)
    
    @test
    def TokenInfo_contains_the_given_refresh_key(self):
        self.assertEqual(self.tokeninfo.refresh_key, 'refresh_key')
    
    @test
    def TokenInfo_refresh_key_is_unique(self):
        self.assertEquals(self.tokeninfo, TokenInfo.new('refresh_key'))

    @test
    def TokenInfo_can_be_retrieved_by_refresh_key(self):
        self.assertEquals(self.tokeninfo, TokenInfo.getExisting('refresh_key'))

    @test
    def getExisting_returns_None_for_nonexisting_refresh_key(self):
        self.assertEquals(None, TokenInfo.getExisting('nonexisting'))

if __name__ == "__main__":
    main()