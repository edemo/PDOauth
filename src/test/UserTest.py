# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from test.helpers.UserUtil import UserUtil
from test.helpers.PDUnitTest import PDUnitTest
from pdoauth.models.User import User
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.ReportedError import ReportedError
from pdoauth.Messages import noHashGiven

class UserTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def setUp(self):
        self.User_can_be_created()
        PDUnitTest.setUp(self)

    def User_can_be_created(self):
        self.setupRandom()
        self.user = User.new("testemail-{0}@example.com".format(self.randString))

    
    def test_User_id_is_returned_by_get_id(self):
        theid = self.user.userid
        self.assertEqual(theid, self.user.get_id())

    
    def test_User_email_with_plus_sign_is_stored_correctly(self):
        email = "test+{0}@example.com".format(self.randString)
        user = User.new(email, None)
        user2 = User.getByEmail(email)
        self.assertEqual(user2.email, email)
        self.assertTrue("+" in user2.email)
        user.rm()
        
    
    def test_User_is_created_as_inactive(self):
        self.assertEqual(False, self.user.is_active())
        
    
    def test_User_is_created_as_unauthenticated(self):
        self.assertEqual(False, self.user.is_authenticated)

    
    def test_Inactive_user_is_loaded_as_inactive(self):
        self.assertEqual(False, User.get(self.user.userid).is_active())
        
    
    def test_Unauthenticated_user_is_loaded_as_unauthenticated(self):
        self.assertEqual(False, User.get(self.user.userid).is_authenticated)

    
    def test_User_can_be_activated(self):
        self.user.activate()
        self.assertEqual(True, self.user.is_active())
        
    
    def test_User_can_be_set_as_authenticated(self):
        self.user.set_authenticated()
        self.assertEqual(True, self.user.is_authenticated)

    
    def test_User_can_be_created_with_credentials(self):
        self.createUserWithCredentials()
    
    
    def test_User_can_be_retrieved_by_id(self):
        self.assertEqual(self.user, User.get(self.user.userid))
    
    
    def test_User_email_is_be_stored(self):
        self.setupUserCreationData()
        cred = CredentialManager.create_user_with_creds(
            'password',
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail)
        self.assertEqual(cred.user.email, self.userCreationEmail)

    
    def test_User_with_credential_can_be_deleted(self):
        self.setupUserCreationData()
        cred = CredentialManager.create_user_with_creds(
            'password',
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail)
        cred.user.rm()
        
    
    def test_User_hash_can_be_stored(self):
        self.setupUserCreationData()
        digest = self.createHash()
        cred = CredentialManager.create_user_with_creds(
            'password',
            self.userCreationUserid,
            self.usercreationPassword,
            self.userCreationEmail,
            digest)
        self.assertEqual(cred.user.hash, digest)

    
    def test_cannot_create_user_with_already_existing_email(self):
        self.createUserWithCredentials()
        self.assertReportedError(User.new, [self.userCreationEmail], 400, ['There is already a user with that email'])

    
    def test_getByDigest_does_not_allow_empty_digest(self):
        with self.assertRaises(ReportedError) as context:
            User.getByDigest('')
        self.assertEqual(noHashGiven,context.exception.descriptor)

    
    def test_getByDigest_does_not_allow_null_digest(self):
        with self.assertRaises(ReportedError) as context:
            User.getByDigest(None)
        self.assertEqual(noHashGiven,context.exception.descriptor)
