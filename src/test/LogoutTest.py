
from twatson.unittest_annotations import Fixture, test
import config
from pdoauth.app import app
from test.helpers.todeprecate.UserTesting import UserTesting

class LogoutTest(Fixture, UserTesting):

    @test
    def you_can_log_out(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get(config.base_url + "/logout")
            self.assertEquals(resp.status_code, 200)
            self.assertEqual('{"message": "logged out"}', self.getResponseText(resp))

    @test
    def you_have_to_be_logged_in_to_log_out(self):
        with app.test_client() as c:
            resp = c.get(config.base_url + "/logout")
            self.assertEquals(resp.status_code, 302)

    @test
    def if_you_log_out_you_will_be_logged_out(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get(config.base_url + "/logout")
            self.assertEquals(resp.status_code, 200)
            resp = c.get(config.base_url + "/logout")
            self.assertEquals(resp.status_code, 302)
