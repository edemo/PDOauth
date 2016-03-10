from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest.helpers.UserTesting import UserTesting, app
import json
from pdoauth.models.Application import Application

class UserinfoIntegrationTest(IntegrationTest, UserTesting):

    @test
    def users_without_login_cannot_get_user_by_email(self):
        self.createUserWithCredentials()
        email = self.userCreationEmail
        with app.test_client() as c:
            self.login(c)
            resp = c.get("/v1/user_by_email/{0}".format(email))
            self.assertEquals(resp.status_code, 403)
            self.assertEquals(self.getResponseText(resp), '{"errors": ["no authorization"]}')

    @test
    def logged_in_users_can_get_their_app_list(self):
        self.createUserWithCredentials()
        with app.test_client() as c:
            self.login(c)
            resp = c.get("/v1/getmyapps")
            self.assertEquals(resp.status_code, 200)
            text = self.getResponseText(resp)
            appList = json.loads(text)
            for entry in appList:
                theApp = Application.find(entry['name'])
                self.assertEqual(entry['hostname'], theApp.redirect_uri.split('/')[2])
