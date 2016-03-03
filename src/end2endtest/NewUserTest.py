from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil

class NewUserTest(BrowsingUtil, Fixture):

    def setUp(self):
        self.setupRandom()
        self.setupUserCreationData()
    
    @test
    def unregistered_user_can_register_with_password_in_the_middle_of_login_procedure_of_a_served_application(self):
        self.callOauthUri()
        self.registerUser()
        self.assertReachedRedirectUri()

    @test
    def unregistered_user_can_register_with_facebook_in_the_middle_of_login_procedure_of_a_served_application(self):
        self.callOauthUri()
        self.handleFbRegistration()
        self.assertReachedRedirectUri()

    def tearDown(self):
        self.removeFbuser()
        self.logoutFromFacebook()
        BrowsingUtil.tearDown(self)