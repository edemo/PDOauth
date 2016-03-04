# -*- coding: UTF-8 -*-
# pylint: disable=maybe-no-member
from pdoauth.app import app
from integrationtest import config
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
import json
from pdoauth.models.Application import Application

class MainTest(IntegrationTest, UserTesting):

    @test
    def root_uri_have_no_function(self):
        resp = app.test_client().get("/")
        self.assertEquals(resp.status_code, 404,)

    @test
    def static_files_are_served(self):
        with app.test_client() as client:
            resp = client.get(config.BASE_URL + "/static/login.html")
            self.assertEqual(resp.status_code,200)

    @test
    def stats_are_available(self):
        with app.test_client() as client:
            resp = client.get(config.BASE_URL + "/v1/statistics")
            self.assertEqual(resp.status_code,200)

    @test
    def getstatsAsJson_gives_the_statistics_in_json(self):
        applicationCount = Application.getStats()
        with app.test_client() as client:
            resp = client.get(config.BASE_URL + "/v1/statistics")
        self.stats=json.loads(resp.data)
        self.assertEqual(self.stats['applications'],applicationCount)
