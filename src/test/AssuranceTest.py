#pylint: disable=line-too-long
from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Assurance import Assurance
from test.helpers.FakeInterFace import FakeForm
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.Messages import otherUsersWithYourHash, addedAssurance
from pdoauth.ReportedError import ReportedError
from pdoauth.models.User import User
from test import config
from pdoauth.EmailHandling import EmailData

class AssuranceTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def prepareLoginForm(self,
            noTestAdderAssurance=False,
            email =None,
            noAssurerAssurance=False,
            digest=None):
        self.createLoggedInUser()
        user = self.cred.user
        if not noAssurerAssurance:
            Assurance.new(user, 'assurer', user)
        if not noTestAdderAssurance:
            Assurance.new(user, 'assurer.test', user)

        self.targetUser = self.createUserWithCredentials().user
        self.targetUser.hash = self.createHash()
        self.digest = self.targetUser.hash
        self.data = dict(
                assurance='test',
                email = None)
        self.addDataBasedOnOptionValue('email', email, self.targetUser.email)
        self.addDataBasedOnOptionValue('digest', digest, self.targetUser.hash)

        form = FakeForm(self.data)
        return form

    def prepareHashCollision(self, assuredTarget, email=None):
        form = self.prepareLoginForm(email=email)
        self.anotherUser = self.createUserWithCredentials().user
        self.anotherUser.hash = self.targetUser.hash
        if assuredTarget:
            Assurance.new(self.anotherUser, 'test', self.cred.user)
        return form

    def doHashCollision(self, assuredTarget=True):
        form = self.prepareHashCollision(assuredTarget)
        self.exception = None
        if assuredTarget:
            with self.assertRaises(ReportedError) as raisedException:
                self.controller.doAddAssurance(form)
            self.exception = raisedException.exception
        else:
            resp = self.controller.doAddAssurance(form)
            data = self.fromJson(resp)
            self.additionalInfo = data['message']
            return resp
    
    def test_assurers_with_appropriate_credential_can_add_assurance_to_user_using_hash(self):
        form = self.prepareLoginForm()
        self.controller.doAddAssurance(form)
        self.assertEqual(Assurance.listByUser(self.targetUser)[0].name, 'test')

    
    def test_adding_assurance_is_possible_using_the_hash_only(self):
        form = self.prepareLoginForm(email = False)
        self.controller.doAddAssurance(form)
        self.assertEqual(Assurance.listByUser(self.targetUser)[0].name, 'test')

    
    def test_assurers_need_assurer_assurance(self):
        form = self.prepareLoginForm(noAssurerAssurance=True)
        self.assertReportedError(
            self.controller.doAddAssurance,[form], 403, ["no authorization"])

    
    def test_assurers_need_giving_assurance(self):
        "that is they have to have assurance.[the assurance to give]"
        form = self.prepareLoginForm(noTestAdderAssurance=True)
        self.assertReportedError(
            self.controller.doAddAssurance,[form], 403, ["no authorization"])
    
    def test_when_an_assurer_wants_to_add_an_assurance_for_a_user_with_hash_and_without_email___and_there_are_multiple_users_with_that_hash___then_an_error_is_signaled(self):
        form = self.prepareHashCollision(False, False)
        self.assertReportedError(
            self.controller.doAddAssurance,[form],
            400, ["More users with the same hash; specify both hash and email"])

    def test_adding_assurance_with_invalid_hash_and_email_fails(self):
        badhash = self.createHash()
        form = self.prepareLoginForm(digest=badhash)
        self.assertReportedError(
            self.controller.doAddAssurance,[form],
            400, ['This user does not have that digest'])
        self.assertFalse('test' in Assurance.getByUser(self.targetUser))

    
    def test_adding_assurance_with_invalid_hash_and_no_email_fails(self):
        badhash = self.createHash()
        form = self.prepareLoginForm(digest=badhash,email=False)
        self.assertReportedError(
            self.controller.doAddAssurance,[form],
            400, ['No user with this hash'])
        self.assertFalse('test' in Assurance.getByUser(self.targetUser))

    def test_in_assured_collision_an_email_is_sent_to_the_other_user_with_HASHCOLLISION_INASSURANCE_config(self):
        self.doHashCollision()
        message = self.controller.mail.outbox[0]
        ed = EmailData(self.anotherUser.email, None, None, [])

        self.assertEqual(message.body,config.Config.HASHCOLLISION_INASSURANCE_EMAIL_BODY_TEXT.format(ed))
        self.assertEqual(message.html,config.Config.HASHCOLLISION_INASSURANCE_EMAIL_BODY_HTML.format(ed))
        self.assertEqual(message.recipients,[self.anotherUser.email])

    def test_in_assured_collision_an_error_message_is_shown(self):
        self.doHashCollision()
        self.assertEqual(otherUsersWithYourHash, self.exception.descriptor[0])
        
    def test_in_assured_collision_the_operation_fails(self):
        self.doHashCollision()
        self.assertEqual(ReportedError, type(self.exception))
        
    def test_in_assured_collision_no_user_gets_deleted(self):
        self.doHashCollision()
        self.assertEqual(self.cred.user.email, User.getByEmail(self.cred.user.email).email)
        self.assertEqual(self.targetUser.email, User.getByEmail(self.targetUser.email).email)
        self.assertEqual(self.anotherUser.email, User.getByEmail(self.anotherUser.email).email)

    def test_in_assured_collision_the_hash_of_the_user_is_deleted(self):
        self.doHashCollision()
        assurances = Assurance.getByUser(self.anotherUser)
        assurer = assurances['test'][0]['assurer']
        self.assertEqual(assurer, self.controller.getCurrentUser().email)
        self.assertEqual(self.targetUser.hash, self.digest)
        self.assertEqual(self.anotherUser.hash, None)

    def test_in_unassured_collision_no_email_sent(self):
        self.doHashCollision(assuredTarget=False)
        messages = self.controller.mail.outbox
        self.assertEqual(0, len(messages))

    def test_in_unassured_collision_the_hash_of_the_user_is_deleted(self):
        self.doHashCollision(assuredTarget=False)
        self.assertEqual(self.targetUser.hash, self.digest)
        self.assertEqual(self.anotherUser.hash, None)

    def test_in_unassured_collision_a_warning_message_is_shown(self):
        resp = self.doHashCollision(assuredTarget=False)
        data = self.fromJson(resp)
        self.assertEqual(addedAssurance, data["message"][0])
        self.assertEqual("1", data["message"][3])

    def test_in_unassured_collision_the_operation_succeeds(self):
        self.doHashCollision(assuredTarget=False)
        self.assertEqual(None, self.exception)

    def test_in_unassured_collision_no_user_gets_deleted(self):
        self.doHashCollision(assuredTarget=False)
        self.assertEqual(self.cred.user.email, User.getByEmail(self.cred.user.email).email)
        self.assertEqual(self.targetUser.email, User.getByEmail(self.targetUser.email).email)
        self.assertEqual(self.anotherUser.email, User.getByEmail(self.anotherUser.email).email)
    
    def test_adding_assurance_with_email_and_hash_of_someone_other_fails(self):
        otherHash = self.createHash()
        form = self.prepareLoginForm(digest=otherHash)
        self.anotherUser = self.createUserWithCredentials().user
        self.anotherUser.hash = otherHash
        self.assertReportedError(
            self.controller.doAddAssurance,[form],
            400, ['This user does not have that digest'])
        self.assertFalse('test' in Assurance.getByUser(self.targetUser))
