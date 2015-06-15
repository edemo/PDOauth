from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Assurance import Assurance
from test.helpers.FakeInterFace import FakeForm
from test.helpers.CryptoTestUtil import CryptoTestUtil

class AssuranceTest(PDUnitTest, UserUtil, CryptoTestUtil):
    
    def _prepareTest(self, noTestAdderAssurance=False, email = None, noAssurerAssurance=False, digest = None):
        self.createLoggedInUser()
        user = self.cred.user
        if not noAssurerAssurance:
            Assurance.new(user, 'assurer', user)
        if not noTestAdderAssurance:
            Assurance.new(user, 'assurer.test', user)
        self.target = self.createUserWithCredentials().user
        self.target.hash = self.createHash()
        self.data = dict(
                assurance='test',
                email = None)
        self.addDataBasedOnOptionValue('email', email, self.target.email)
        self.addDataBasedOnOptionValue('digest', digest, self.target.hash)
        form = FakeForm(self.data)
        return form

    @test
    def assurers_with_appropriate_credential_can_add_assurance_to_user_using_hash(self):
        form = self._prepareTest()
        self.controller.do_add_assurance(form)
        self.assertEqual(Assurance.listByUser(self.target)[0].name, 'test')

    @test
    def adding_assurance_is_possible_using_the_hash_only(self):
        form = self._prepareTest(email = False)
        self.controller.do_add_assurance(form)
        self.assertEqual(Assurance.listByUser(self.target)[0].name, 'test')

    @test
    def assurers_need_assurer_assurance(self):
        form = self._prepareTest(noAssurerAssurance=True)
        self.assertReportedError(self.controller.do_add_assurance,[form], 403, ["no authorization"])

    @test
    def assurers_need_giving_assurance(self):
        "that is they have to have assurance.[the assurance to give]"
        form = self._prepareTest(noTestAdderAssurance=True)
        self.assertReportedError(self.controller.do_add_assurance,[form], 403, ["no authorization"])

    def _prepareHashCollision(self, email=None):
        form = self._prepareTest(email=email)
        self.digest = self.target.hash
        self.anotherUser = self.createUserWithCredentials().user
        self.anotherUser.hash = self.digest
        return form

    @test
    def when_an_assurer_wants_to_add_an_assurance_for_a_user_with_hash_and_without_email___and_there_are_multiple_users_with_that_hash___then_an_error_is_signaled(self):
        form = self._prepareHashCollision(False)
        self.assertReportedError(self.controller.do_add_assurance,[form], 400, ["More users with the same hash; specify both hash and email"])

    @test
    def when_an_assurance_added_with_hash_and_email___and_there_is_another_user_with_the_same_hash___the_hash_from_the_other_user_is_deleted(self):
        form = self._prepareHashCollision()
        resp = self.controller.do_add_assurance(form)
        self.assertEquals(200, resp.status_code)
        self.assertEquals(Assurance.getByUser(self.target)['test'][0]['assurer'], self.controller.getCurrentUser().email)
        self.assertEqual(self.anotherUser.hash, None)
        self.assertEqual(self.target.hash, self.digest)

    @test
    def adding_assurance_with_invalid_hash_and_email_fails(self):
        badhash = self.createHash()
        form = self._prepareTest(digest=badhash)
        self.assertReportedError(self.controller.do_add_assurance,[form], 400, ['This user does not have that digest'])
        self.assertFalse(Assurance.getByUser(self.target).has_key('test'))
    
    @test
    def adding_assurance_with_invalid_hash_and_no_email_fails(self):
        badhash = self.createHash()
        form = self._prepareTest(digest=badhash,email=False)
        self.assertReportedError(self.controller.do_add_assurance,[form], 400, ['No user with this hash'])
        self.assertFalse(Assurance.getByUser(self.target).has_key('test'))

    @test
    def adding_assurance_with_email_and_hash_of_someone_other_fails(self):
        otherHash = self.createHash()
        form = self._prepareTest(digest=otherHash)
        self.anotherUser = self.createUserWithCredentials().user
        self.anotherUser.hash = otherHash
        self.assertReportedError(self.controller.do_add_assurance,[form], 400, ['This user does not have that digest'])
        self.assertFalse(Assurance.getByUser(self.target).has_key('test'))
