from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil

class LoginTest(PDUnitTest, UserUtil):
    @test
    def password_login_works_with_username_and_password(self):
        form = self.prepareLoginForm()
        self.controller.doLogin(form)
        self.assertTrue(self.userCreationEmail, self.controller.getCurrentUser().email)

    @test
    def login_sets_the_csrf_cookie(self):
        form = self.prepareLoginForm()
        resp = self.controller.doLogin(form)
        self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))

    @test
    def inactive_user_cannot_authenticate(self):
        form = self.prepareLoginForm(inactive = True)
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Inactive or disabled user"])

    @test
    def authentication_with_bad_userid_is_rejected(self):
        form = self.prepareLoginForm(identifier = 'baduser')
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Bad username or password"])

    @test
    def authentication_with_bad_secret_is_rejected(self):
        form = self.prepareLoginForm(secret = self.mkRandomPassword())
        self.assertReportedError(self.controller.doLogin, [form], 403, ["Bad username or password"])
