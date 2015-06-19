from integrationtest import config
from pdoauth.app import app
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class LogoutTest(IntegrationTest, UserTesting):

    @test
    def you_can_log_out(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.get(config.BASE_URL + "/logout")
            self.assertEquals(resp.status_code, 200)
            self.assertEqual('{"message": "logged out"}', self.getResponseText(resp))

    @test
    def you_have_to_be_logged_in_to_log_out(self):
        with app.test_client() as client:
            resp = client.get(config.BASE_URL + "/logout")
            self.assertEquals(resp.status_code, 403)

    @test
    def if_you_log_out_you_will_be_logged_out(self):
        with app.test_client() as client:
            self.login(client)
            resp = client.get(config.BASE_URL + "/logout")
            self.assertEquals(resp.status_code, 200)
            resp = client.get(config.BASE_URL + "/logout")
            self.assertEquals(resp.status_code, 403)
