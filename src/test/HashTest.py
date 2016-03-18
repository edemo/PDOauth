from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.FakeInterFace import FakeForm
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.models.Assurance import Assurance

class HashTest(PDUnitTest, UserUtil, CryptoTestUtil):
    @test
    def if_hash_is_same_no_assurances_deleted(self):
        digest = self.createHash()
        user = self.createUserWithCredentials().user
        data = dict(
            digest=digest
            )
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        Assurance.new(user, "test", user)
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        assurances = Assurance.getByUser(user)
        self.assertTrue("test" in assurances.keys())
        self.assertTrue("hashgiven" in assurances.keys())
