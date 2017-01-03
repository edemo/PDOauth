from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.UserUtil import UserUtil
from test.helpers.FakeInterFace import FakeForm
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.models.Assurance import Assurance
from pdoauth.ReportedError import ReportedError
from pdoauth.models.User import User
from pdoauth.models.AppMap import AppMap
from pdoauth.models.Application import Application
from pdoauth.Messages import sameHash, anotherUserUsingYourHash
from test import config
from pdoauth.EmailHandling import EmailData

class HashTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def unAssuredCollision(self):
        digest, anotheruser = self.createUnassuredUser()
        user = self.createUserWithCredentials().user
        user.hash = digest
        user.save()
        additionalInfo = dict()
        self.controller.checkHashInOtherUsers(user, additionalInfo, digest)
        self.additionalInfo = additionalInfo
        self.exception = None
        return anotheruser

    def assuredCollision(self):
        digest, anotheruser = self.createAssuredUser()
        user = self.createUserWithCredentials().user
        additionalInfo = dict()
        with self.assertRaises(ReportedError) as cm:
            self.controller.checkHashInOtherUsers(user, additionalInfo, digest)
        self.exception = cm.exception
        self.additionalInfo = additionalInfo
        return anotheruser
    
    def test_if_hash_is_same_no_assurances_deleted(self):
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

    
    def test_if_hash_is_same_a_message_is_sent(self):
        digest = self.createHash()
        user = self.createUserWithCredentials().user
        data = dict(
            digest=digest
            )
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        resp = self.controller.checkAndUpdateHash(FakeForm(data), user)
        self.assertEqual(sameHash, resp['message'])

    
    def test_if_hash_is_same_but_empty__no_message(self):
        digest = ""
        user = self.createUserWithCredentials().user
        data = dict(
            digest=digest
            )
        self.controller.checkAndUpdateHash(FakeForm(data), user)
        resp = self.controller.checkAndUpdateHash(FakeForm(data), user)
        self.assertEqual(dict(), resp)
        
    
    def test_in_hash_collision_if_the_other_user_is_hand_assured_the_user_is_not_deleted(self):
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
        self.assertEqual(email, User.getByEmail(email).email)

    def test_in_assured_hash_collision_an_email_is_sent_to_the_other_user_with_HASHCOLLISION_ASSURED_config(self):
        anotheruser=self.assuredCollision()
        message = self.controller.mail.outbox[0]
        ed = EmailData(anotheruser.email, None, None, [])
        self.assertEqual(message.body,config.Config.HASHCOLLISION_ASSURED_EMAIL_BODY_TEXT.format(ed))
        self.assertEqual(message.html,config.Config.HASHCOLLISION_ASSURED_EMAIL_BODY_HTML.format(ed))
        self.assertEqual(message.recipients,[anotheruser.email])
        
    def test_in_assured_hash_collision_an_error_message_states_what_happened(self):
        self.assuredCollision()
        self.assertEqual([anotherUserUsingYourHash], self.exception.descriptor)
        
    def test_in_assured_hash_collision_the_operation_fails(self):
        self.assuredCollision()
        self.assertNotEqual(None, self.exception)
        
    def test_in_assured_hash_collision_no_user_deleted(self):
        anotheruser=self.assuredCollision()
        email = self.userCreationEmail
        self.assertEqual(email, User.getByEmail(email).email)
        self.assertEqual(anotheruser.email, User.getByEmail(anotheruser.email).email)
        
    def test_in_unassured_hash_collision_an_email_is_sent_to_the_other_user_with_HASHCOLLISION_UNASSURED_config(self):
        anotheruser=self.unAssuredCollision()
        message = self.controller.mail.outbox[0]
        ed = EmailData(anotheruser.email, None, None, [])
        self.assertEqual(message.body,config.Config.HASHCOLLISION_UNASSURED_EMAIL_BODY_TEXT.format(ed))
        self.assertEqual(message.html,config.Config.HASHCOLLISION_UNASSURED_EMAIL_BODY_HTML.format(ed))
        self.assertEqual(message.recipients,[anotheruser.email])
        
    def test_in_unassured_hash_collision_a_warning_message_states_what_happened(self):
        self.unAssuredCollision()
        self.assertEqual(anotherUserUsingYourHash, self.additionalInfo['message'])

    def test_in_unassured_hash_collision_the_operation_succeeds(self):
        self.unAssuredCollision()
        self.assertEqual(None, self.exception)

    def test_in_unassured_hash_collision_no_user_is_deleted(self):
        anotheruser = self.unAssuredCollision()
        email = self.userCreationEmail
        self.assertEqual(email, User.getByEmail(email).email)
        self.assertEqual(anotheruser.email, User.getByEmail(anotheruser.email).email)
        