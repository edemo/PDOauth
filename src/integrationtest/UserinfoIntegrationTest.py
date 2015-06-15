from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest.helpers.UserTesting import UserTesting, app

class UserinfoIntegrationTest(IntegrationTest, UserTesting):

    @test
    def users_without_login_cannot_get_user_by_email(self):
        self.createUserWithCredentials()
        email = self.usercreation_email
        with app.test_client() as c:
            self.login(c)
            resp = c.get("/v1/user_by_email/{0}".format(email))
            self.assertEquals(resp.status_code, 403)
            self.assertEquals(self.getResponseText(resp), '{"errors": ["no authorization"]}')
