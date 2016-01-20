#pylint: disable=no-member
from twatson.unittest_annotations import Fixture, test
from test.helpers.RandomUtil import RandomUtil
from pdoauth.models.Application import Application
from pdoauth.models.AppAssurance import AppAssurance
import applicationtool
import sys
import io

class ApplicationToolTest(Fixture, RandomUtil):

    def runApplicationToolWithParameters(self,parameters):
        out=io.BytesIO()
        tempout=sys.stdout
        sys.stdout=out
        err=io.BytesIO()
        temperr=sys.stderr
        sys.stderr=err
        systemExit=False
        try:
            applicationtool.main(parameters)
        except SystemExit:
            systemExit=True
        sys.stdout=tempout
        sys.stderr=temperr
        return (out,err,systemExit)

    @test
    def applicationtool_gives_error_if_no_parameters_are_given(self):
        out, err, isExit = self.runApplicationToolWithParameters([])
        self.assertTrue(isExit)
        self.assertTrue( 'error: too few arguments' in err.getvalue())
        self.assertTrue( 'usage:' in err.getvalue())

    @test
    def applicationtool_gives_help_for_dash_dash_help(self):
        out, err, isExit = self.runApplicationToolWithParameters(["--help"])
        self.assertTrue(isExit)
        self.assertTrue( 'usage:' in out.getvalue())

    @test
    def applicationtool_works_with_a_name_a_https_redrect_uri_a_secret_and_an_assurance(self):
        appname = self.mkRandomString(6)
        password = self.mkRandomPassword()
        uri = "https://%s.org/"%(appname)
        out, err, isExit = self.runApplicationToolWithParameters([appname, password, uri, 'test'])
        self.assertFalse(isExit)
        outStr = out.getvalue()
        self.assertEqual("", err.getvalue())
        self.assertTrue( 'id of the app is:' in outStr)
        appId = outStr.split(": ")[1].strip()
        app = Application.find(appname)
        self.assertEquals(app.appid, appId)
        self.assertEquals(app.secret, password)
        self.assertEquals(app.redirect_uri, uri)
        self.assertEquals(AppAssurance.get(app), ['test'])

    @test
    def applicationtool_works_with_a_name_a_https_redrect_uri_a_secret_and_two_assurances(self):
        appname = self.mkRandomString(6)
        password = self.mkRandomPassword()
        uri = "https://%s.org/"%(appname)
        out, err, isExit = self.runApplicationToolWithParameters([appname, password, uri, 'test', 'test2'])
        self.assertFalse(isExit)
        outStr = out.getvalue()
        self.assertTrue( 'id of the app is:' in outStr)
        appId = outStr.split(": ")[1].strip()
        app = Application.find(appname)
        self.assertEquals(app.appid, appId)
        self.assertEquals(app.secret, password)
        self.assertEquals(app.redirect_uri, uri)
        self.assertEquals(AppAssurance.get(app), ['test','test2'])

    @test
    def applicationtool_refuses_http_uri(self):
        appname = self.mkRandomString(6)
        password = self.mkRandomPassword()
        uri = "http://%s.org/"%(appname)
        out, err, isExit = self.runApplicationToolWithParameters([appname, password, uri, 'test', 'test2'])
        errStr = err.getvalue()
        self.assertTrue( 'NonHttpsRedirectUri' in errStr)

