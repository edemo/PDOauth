# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from test.helpers.UserUtil import UserUtil
from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.models.User import User
from test.helpers.CryptoTestUtil import CryptoTestUtil

class UserTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def setUp(self):
        self.User_can_be_created()

    def User_can_be_created(self):
        self.setupRandom()
        self.user = User.new("testemail-{0}@example.com".format(self.randString))

    @test
    def User_id_is_returned_by_get_id(self):
        theid = self.user.userid
        self.assertEquals(theid, self.user.get_id())

    @test
    def User_email_with_plus_sign_is_stored_correctly(self):
        email = "test+{0}@example.com".format(self.randString)
        user = User.new(email, None)
        user2 = User.getByEmail(email)
        self.assertEquals(user2.email, email)
        self.assertTrue("+" in user2.email)
        user.rm()
        
    @test
    def User_is_created_as_inactive(self):
        self.assertEqual(False, self.user.is_active())
        
    @test
    def User_is_created_as_unauthenticated(self):
        self.assertEqual(False, self.user.is_authenticated())

    @test
    def Inactive_user_is_loaded_as_inactive(self):
        self.assertEqual(False, User.get(self.user.userid).is_active())
        
    @test
    def Unauthenticated_user_is_loaded_as_unauthenticated(self):
        self.assertEqual(False, User.get(self.user.userid).is_authenticated())

    @test
    def User_can_be_activated(self):
        self.user.activate()
        self.assertEqual(True, self.user.is_active())
        
    @test
    def User_can_be_set_as_authenticated(self):
        self.user.set_authenticated()
        self.assertEqual(True, self.user.is_authenticated())

    @test
    def User_can_be_created_with_credentials(self):
        self.createUserWithCredentials()
    
    @test
    def User_can_be_retrieved_by_id(self):
        self.assertEqual(self.user, User.get(self.user.userid))
    
    @test
    def User_email_is_be_stored(self):
        self.setupUserCreationData()
        cred = CredentialManager.create_user_with_creds(
            'password',
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail)
        self.assertEquals(cred.user.email, self.userCreationEmail)
    
    @test
    def User_hash_can_be_stored(self):
        self.setupUserCreationData()
        digest = self.createHash()
        cred = CredentialManager.create_user_with_creds(
            'password',
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail,
            digest)
        self.assertEquals(cred.user.hash, digest)

    @test
    def cannot_create_user_with_already_existing_email(self):
        self.createUserWithCredentials()
        self.assertReportedError(User.new, [self.userCreationEmail], 400, ['there is already a user with this email'])

    @test
    def getByDigest_does_not_allow_empty_digest(self):
        self.assertRaises(ValueError, User.getByDigest,'')

    @test
    def getByDigest_does_not_allow_null_digest(self):
        self.assertRaises(ValueError, User.getByDigest,None)
