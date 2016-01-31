# -*- coding: UTF-8 -*-
# pylint: disable=no-member, invalid-name
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from urllib import urlencode
from pdoauth.FlaskInterface import FlaskInterface
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest import config

class AuthProviderIntegrationTest(IntegrationTest, UserTesting):

    def setUp(self):
        self.setupRandom()
        #Application.query.delete()  # @UndefinedVariable
        #KeyData.query.delete()  # @UndefinedVariable
        #TokenInfoByAccessKey.query.delete()  # @UndefinedVariable
        self.authProvider = AuthProvider(FlaskInterface())
        self.session = db.session
        self.app = Application.new(
            "test app %s"%(self.mkRandomString(5)),
            self.mkRandomPassword(),
            "https://test.app/redirecturi")
        self.session.add(self.app)
        self.session.commit()

    def tearDown(self):
        self.session.close()


    @test
    def authorization_code_cannot_be_obtained_without_user(self):
        with app.test_client() as c:
            redirect_uri = 'https://test.app/redirecturi'
            params = {
                    "response_type":"code",
                    "client_id":self.app.appid,
                    "redirect_uri":redirect_uri
            }
            resp = c.get("https://localhost.local/v1/oauth2/auth", query_string=params)
            denyUri = config.BASE_URL
            self.assertTrue(resp.headers['Location'].startswith(denyUri))

    @test
    def auth_interface_redirects_to_redirect_uri(self):
        params = {
            "response_type": "code",
            "client_id": self.app.name,
            "redirectUri": self.app.redirect_uri
        }
        baseUrl = app.config.get('BASE_URL')
        uriBase = "/v1/oauth2/auth"
        queryString = urlencode(params)
        with app.test_client() as client:
            resp = client.get(
                    uriBase, query_string=queryString, base_url=baseUrl)
            theUri = baseUrl + uriBase
            targetUri = "{0}?{1}".format(
                app.config.get('START_URL'),
                urlencode({"next": "{0}?{1}".format(theUri, queryString)})
            )
        self.assertEquals(resp.status_code, 302)
        self.assertEquals(resp.headers['Location'],targetUri)
