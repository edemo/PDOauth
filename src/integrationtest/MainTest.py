# -*- coding: UTF-8 -*-
from pdoauth.app import app
import config
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test

class MainTest(IntegrationTest, UserTesting):

    @test
    def NoRootUri(self):
        resp = app.test_client().get("/")
        self.assertEquals(resp.status_code, 404,)

    @test
    def static_files_are_served(self):
        with app.test_client() as c:
            resp = c.get(config.base_url + "/static/login.html")
            self.assertEqual(resp.status_code,200)
