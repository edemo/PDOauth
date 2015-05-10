from twatson.unittest_annotations import Fixture, test
from test.TestUtil import UserTesting, CSRFMixin
from flask import json
from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.CredentialManager import CredentialManager

class PasswordChangeTest(Fixture, UserTesting, CSRFMixin):


    def preparePasswordChangeTest(self, c):
        resp = self.login(c)
        self.assertUserResponse(resp)

    def doPasswordChange(self, c, csrf=None, oldPassword=None, newPassword=None):
        if csrf is None:
            csrf = self.getCSRF(c)
        if oldPassword is None:
            oldPassword = self.usercreation_password
        if newPassword is None:
            newPassword="n3wp4ssw0rd.{0}".format(self.randString)
        self.newPassword = newPassword
        data = dict(
            csrf_token=csrf,
            newPassword=newPassword)
        if oldPassword != "skip":
            data['oldPassword'] = oldPassword
        resp = c.post("http://localhost.local/v1/users/me/change_password", data=data)
        return resp

    @test
    def change_password_returns_200_and_a_success_message(self):
        with app.test_client() as c:
            self.preparePasswordChangeTest(c)
            resp = self.doPasswordChange(c)
            self.assertEquals(resp.status_code, 200)
            respdata = json.loads(self.getResponseText(resp))
            self.assertEqual(respdata['message'], 'pasword changed succesfully')

    @test
    def change_password_does_change_password(self):
        with app.test_client() as c:
            self.preparePasswordChangeTest(c)
            self.doPasswordChange(c)
            cred = Credential.get('password', self.usercreation_userid)
            self.assertEquals(cred.secret, CredentialManager.protect_secret(self.newPassword))

    @test
    def change_password_needs_csrf(self):
        with app.test_client() as c:
            self.preparePasswordChangeTest(c)
            resp = self.doPasswordChange(c,csrf="badcsrf")
            self.assertEquals(resp.status_code, 400)
            respdata = json.loads(self.getResponseText(resp))
            self.assertEqual(respdata['errors'], [u'csrf_token: csrf validation error'])
            
    @test
    def change_password_for_self_needs_old_password(self):
        with app.test_client() as c:
            self.preparePasswordChangeTest(c)
            resp = self.doPasswordChange(c, oldPassword='skip')
            self.assertEquals(resp.status_code, 400)
            respdata = json.loads(self.getResponseText(resp))
            self.assertTrue(u'oldPassword: ' in respdata['errors'][0])

    @test
    def old_password_for_self_should_be_correct(self):
        with app.test_client() as c:
            self.preparePasswordChangeTest(c)
            resp = self.doPasswordChange(c, oldPassword='incorrectPassword')
            self.assertEquals(resp.status_code, 400)
            respdata = json.loads(self.getResponseText(resp))
            self.assertEqual(respdata['errors'], ["old password does not match"])
