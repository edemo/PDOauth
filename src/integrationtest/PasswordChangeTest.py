from pdoauth.app import app
from pdoauth.models.Credential import Credential
from pdoauth.CredentialManager import CredentialManager
from integrationtest import config

from integrationtest.helpers.CSRFMixin import CSRFMixin
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class PasswordChangeTest(IntegrationTest, UserTesting, CSRFMixin):

    def _preparePasswordChangeTest(self, client):
        resp = self.login(client)
        self.assertUserResponse(resp)

    def _doPasswordChange(self, client, csrf=None, oldPassword=None, newPassword=None):
        if csrf is None:
            csrf = self.getCSRF(client)
        if oldPassword is None:
            oldPassword = self.usercreationPassword
        if newPassword is None:
            newPassword="n3wp4ssw0rd.{0}".format(self.mkRandomPassword())
        self.newPassword = newPassword
        data = dict(
            csrf_token=csrf,
            newPassword=newPassword)
        if oldPassword != "skip":
            data['oldPassword'] = oldPassword
        resp = client.post(config.BASE_URL + "/v1/users/me/change_password", data=data)
        return resp

    @test
    def change_password_returns_200_and_a_success_message(self):
        with app.test_client() as client:
            self._preparePasswordChangeTest(client)
            resp = self._doPasswordChange(client)
            self.assertEquals(resp.status_code, 200)
            respdata = self.fromJson(resp)
            self.assertEqual(respdata['message'], 'password changed succesfully')

    @test
    def change_password_does_change_password(self):
        with app.test_client() as client:
            self._preparePasswordChangeTest(client)
            self._doPasswordChange(client)
            cred = Credential.get('password', self.userCreationUserid)
            self.assertEquals(cred.secret, CredentialManager.protect_secret(self.newPassword))

    @test
    def change_password_needs_csrf(self):
        with app.test_client() as client:
            self._preparePasswordChangeTest(client)
            resp = self._doPasswordChange(client,csrf="badcsrf")
            self.assertEquals(resp.status_code, 400)
            respdata = self.fromJson(resp)
            self.assertEqual(respdata['errors'], [u'csrf_token: csrf validation error'])

    @test
    def change_password_for_self_needs_old_password(self):
        with app.test_client() as client:
            self._preparePasswordChangeTest(client)
            resp = self._doPasswordChange(client, oldPassword='skip')
            self.assertEquals(resp.status_code, 400)
            respdata = self.fromJson(resp)
            self.assertTrue(u'oldPassword: ' in respdata['errors'][0])

    @test
    def old_password_for_self_should_be_correct(self):
        with app.test_client() as client:
            self._preparePasswordChangeTest(client)
            resp = self._doPasswordChange(client, oldPassword=self.mkRandomPassword())
            self.assertEquals(resp.status_code, 400)
            respdata = self.fromJson(resp)
            self.assertEqual(respdata['errors'], ["old password does not match"])
