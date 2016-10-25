from twatson.unittest_annotations import Fixture
from end2endtest.helpers.BrowsingUtil import BrowsingUtil
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.app import mail

class DigestTest(Fixture, BrowsingUtil, CryptoTestUtil):

    
    def test_you_can_add_a_digest_as_a_logged_in_user(self):
        digest = self.registerAndGiveHash()
        self.waitUntilElementEnabled("viewChangeHashForm")
        self.assertElementMatches("change-hash-form_digest-pre", digest)

    
    def test_you_can_change_the_digest_as_a_logged_in_user(self):
        self.registerAndGiveHash()
        digest=self.changeMyHash()
        self.waitUntilElementEnabled("viewChangeHashForm")
        self.assertElementMatches("change-hash-form_digest-pre", digest)

    
    def test_you_can_delete_the_digest_as_a_logged_in_user_by_giving_empty_one(self):
        self.registerAndGiveHash()
        self.changeMyHash("")
        self.waitUntilElementEnabled("viewChangeHashForm")
        self.assertElementMatches("change-hash-form_digest-pre", '')
        
    def tearDown(self):
        BrowsingUtil.tearDown(self)
