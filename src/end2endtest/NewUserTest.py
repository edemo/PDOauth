from end2endtest.helpers.BrowsingUtil import BrowsingUtil
from unittest.case import TestCase

class NewUserTest(BrowsingUtil, TestCase):

    def setUp(self):
        self.setupRandom()
        self.setupUserCreationData()
    
    
    def test_unregistered_user_can_register_with_password_in_the_middle_of_login_procedure_of_a_served_application(self):
        self.callOauthUri()
        self.registerUser(buttonId='section_changer_register')
        self.assertReachedRedirectUri()

    
    def test_unregistered_user_can_register_with_facebook_in_the_middle_of_login_procedure_of_a_served_application(self):
        self.removeFbuser()
        self.callOauthUri()
        self.handleFbRegistrationAppLogin()
        self.assertReachedRedirectUri()

    def tearDown(self):
        self.removeFbuser()
        self.logoutFromFacebook()
        BrowsingUtil.tearDown(self)
