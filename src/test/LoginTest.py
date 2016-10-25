from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil

class LoginTest(PDUnitTest, UserUtil):
    
    def test_password_login_works_with_username_and_password(self):
        form = self.prepareLoginForm()
        self.controller.doLogin(form)
        self.assertEqual(self.userCreationEmail, self.controller.getCurrentUser().email)

    
    def test_login_sets_the_csrf_cookie(self):
        form = self.prepareLoginForm()
        resp = self.controller.doLogin(form)
        self.assertTrue("csrf=" in resp.headers['Set-Cookie'])

    
    def test_inactive_user_cannot_authenticate(self):
        form = self.prepareLoginForm(inactive = True)
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Inactive or disabled user"])

    
    def test_authentication_with_bad_userid_is_rejected(self):
        form = self.prepareLoginForm(identifier = 'baduser')
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Bad username or password"])

    
    def test_authentication_with_bad_secret_is_rejected(self):
        form = self.prepareLoginForm(secret = self.mkRandomPassword())
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Bad username or password"])

    
    def test_user_can_use_email_with_password_authentication(self):
        form = self.prepareLoginForm()
        form.vals['identifier'].data=self.userCreationEmail
        self.controller.doLogin(form)
        self.assertEqual(self.userCreationEmail, self.controller.getCurrentUser().email)
