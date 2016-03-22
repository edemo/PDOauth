from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.FakeInterFace import FakeForm
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.models.Assurance import Assurance
from pdoauth.ReportedError import ReportedError
from pdoauth.models.User import User
from pdoauth.models.AppMap import AppMap
from pdoauth.models.Application import Application
from pdoauth.Messages import sameHash

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

    @test
    def if_hash_is_same_a_message_is_sent(self):
        digest = self.createHash()
        user = self.createUserWithCredentials().user
        data = dict(
            digest=digest
            )
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        resp = self.controller.checkAndUpdateHash(FakeForm(data), user)
        self.assertEqual(sameHash, resp['message'])

    @test
    def if_hash_is_same_but_empty__no_message(self):
        digest = ""
        user = self.createUserWithCredentials().user
        data = dict(
            digest=digest
            )
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        resp = self.controller.checkAndUpdateHash(FakeForm(data), user)
        self.assertEqual(dict(), resp)
        
    @test
    def in_hash_collision_if_the_other_user_is_hand_assured_the_user_is_deleted(self):
        anotheruser = self.createUserWithCredentials().user
        digest = self.createHash()
        anotheruser.hash = digest
        Assurance.new(anotheruser, "test", anotheruser)
        anotheruser.save()
        user = self.createUserWithCredentials().user
        app = Application.query.first()  # @UndefinedVariable
        AppMap.new(app, user)
        email = self.userCreationEmail
        additionalInfo = dict()
        with self.assertRaises(ReportedError):
            self.controller.checkHashInOtherUsers(user,additionalInfo,digest)
        self.assertEqual(None, User.getByEmail(email))

        