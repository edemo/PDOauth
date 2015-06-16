# -*- coding: UTF-8 -*-
from test.helpers.ServerSide import ServerSide
from integrationtest.helpers.UserTesting import UserTesting
from pdoauth.app import app
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class ServerSideTest(IntegrationTest, ServerSide, UserTesting):

    @test
    def authorization_code_can_be_obtained_by_an_authenticated_user_using_correct_client_id_and_redirect_uri(self):
        self.loginAndGetCode()

    @test
    def you_can_get_user_info_with_authorization_code(self):
        code = self.loginAndGetCode()
        data = self.doServerSideRequest(code)
        headers = {
            'Authorization': '{0} {1}'.format(
                    data['token_type'],
                    data['access_token']
                )
        }
        with app.test_client() as c:
            resp = c.get('/v1/users/me', headers = headers)
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertTrue(data.has_key('userid'))
