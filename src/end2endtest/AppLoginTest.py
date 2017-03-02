from end2endtest.helpers.BrowsingUtil import BrowsingUtil
from unittest.case import TestCase
from pdoauth.CredentialManager import CredentialManager
from end2endtest import config

class AppLoginTest(BrowsingUtil, TestCase):

    def setUp(self):
        self.setupRandom()
        self.setupUserCreationData()
    
    
    def test_user_can_login_with_password_for_a_served_application(self):
        cred=CredentialManager.create_user_with_creds(
                    'password',
                    self.userCreationUserid,
                    self.usercreationPassword,
                    self.userCreationEmail)
        self.callOauthUri()
        self.beginProcess("login with password in app")
        self.fillInField("LoginForm_email_input", self.userCreationUserid)
        self.fillInField("LoginForm_password_input", self.usercreationPassword)
        self.click("loginform_submit-button")
        self.waitForJsState("myApps")
        self.click("acceptance_accept")
        self.endProcess("login with password in app")
        self.assertReachedRedirectUri()
    
    def test_user_can_login_with_facebook_for_a_served_application(self):
        user = config.facebookUser1
        CredentialManager.create_user_with_creds(
                    'facebook',
                    user.userid,
                    user.userid,
                    user.email)
        self.callOauthUri()
        self.pushFbButtonWhenready(buttonId="login_facebook_button")
        self.handleFbLoginPage(user)
        self.waitForJsState('myApps')
        self.click("acceptance_accept")
        self.assertReachedRedirectUri()

    def tearDown(self):
        self.removeFbuser()
        self.logoutFromFacebook()
        BrowsingUtil.tearDown(self)
