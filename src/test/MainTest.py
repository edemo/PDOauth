
from twatson.unittest_annotations import Fixture, test

from pdoauth.app import app

class Test(Fixture):


    def setUp(self):
        self.app = app.test_client()

    @test
    def NoRootUri(self):
        resp = self.app.get("/")
        self.assertEquals(resp.status_code, 404,)
