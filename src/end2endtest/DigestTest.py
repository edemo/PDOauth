from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil
from test.helpers.CryptoTestUtil import CryptoTestUtil

class DigestTest(Fixture, BrowsingUtil, CryptoTestUtil):

    @test
    def you_can_add_a_digest_as_a_logged_in_user(self):
        digest = self.registerAndGiveHash()
        self.assertTextInMeMsg("hash:\n{0}".format(digest))

    @test
    def you_can_change_the_digest_as_a_logged_in_user(self):
        self.registerAndGiveHash()
        digest=self.changeMyHash()
        self.assertTextInMeMsg("hash:\n{0}".format(digest))

    @test
    def you_can_delete_the_digest_as_a_logged_in_user_by_giving_empty_one(self):
        self.registerAndGiveHash()
        self.changeMyHash("")
        self.assertTextInMeMsg("hash:\n{0}".format("null"))
        
    def tearDown(self):
        BrowsingUtil.tearDown(self)
