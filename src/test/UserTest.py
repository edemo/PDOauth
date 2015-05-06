# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.models.User import User
from pdoauth.CredentialManager import CredentialManager
from test.TestUtil import UserTesting

class UserTest(Fixture, UserTesting):

    def setUp(self):
        User.query.delete()  # @UndefinedVariable
        self.User_can_be_created()
        self.setupRandom()

    def User_can_be_created(self):
        self.user = User.new("testemail@example.com")

    @test
    def User_id_is_returned_by_get_id(self):
        theid = self.user.id
        self.assertEquals(theid, self.user.get_id())
        
    @test
    def User_is_created_as_inactive(self):
        self.assertEqual(False, self.user.is_active())
        
    @test
    def User_is_created_as_unauthenticated(self):
        self.assertEqual(False, self.user.is_authenticated())

    @test
    def Inactive_user_is_loaded_as_inactive(self):
        self.assertEqual(False, User.get(self.user.id).is_active())
        
    @test
    def Unauthenticated_user_is_loaded_as_unauthenticated(self):
        self.assertEqual(False, User.get(self.user.id).is_authenticated())

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
        self.create_user_with_credentials()
    
    @test
    def User_can_be_retrieved_by_id(self):
        self.assertEqual(self.user, User.get(self.user.id))
    
    @test
    def User_email_can_be_stored(self):
        user = CredentialManager.create_user_with_creds('password', 'userid', 'password', email="testuser@nowhere.example.com")
        self.assertEquals(user.email, "testuser@nowhere.example.com")
    
    @test
    def User_hash_can_be_stored(self):
        user = CredentialManager.create_user_with_creds('password', 'userid', 'password', email="testuser@nowhere.example.com", digest="xxxxxxxxx")
        self.assertEquals(user.email, "testuser@nowhere.example.com")
