from integrationtest.helpers.IntegrationTest import IntegrationTest
from integrationtest.helpers.UserTesting import UserTesting, app
import json
from pdoauth.models.Application import Application
from test.helpers.AppInfoUtil import AppInfoUtil
from integrationtest.helpers.CSRFMixin import CSRFMixin

class UserinfoIntegrationTest(IntegrationTest, UserTesting, AppInfoUtil, CSRFMixin):

    @classmethod
    def setUpClass(cls):
        AppInfoUtil.setUpClass()

    
    def test_users_cannot_get_another_users_info(self):
        self.createUserWithCredentials()
        email = self.userCreationEmail
        with app.test_client() as c:
            self.login(c)
            resp = c.get("/v1/user_by_email/{0}".format(email))
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(self.getResponseText(resp), '{"errors": ["no authorization"]}')

    
    def test_logged_in_users_can_get_their_app_list(self):
        with app.test_client() as c:
            self.login(c, self.user)
            resp = c.get("/v1/getmyapps")
            self.assertEqual(resp.status_code, 200)
            text = self.getResponseText(resp)
            appList = json.loads(text)
            for entry in appList:
                theApp = Application.find(entry['name'])
                self.assertEqual(entry['hostname'], theApp.redirect_uri.split('/')[2])

    
    def test_logged_in_users_can_disable_an_app_to_send_email_to_them(self):
        self.assertUserSetTheMap(app, False, 'false')

    
    def test_logged_in_users_can_enable_an_app_to_send_email_to_them(self):
        self.assertUserSetTheMap(app, True, 'true')
