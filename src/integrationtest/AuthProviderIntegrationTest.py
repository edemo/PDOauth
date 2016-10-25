# -*- coding: UTF-8 -*-
# pylint: disable=no-member, invalid-name
from integrationtest.helpers.IntegrationTest import IntegrationTest
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from pdoauth.FlaskInterface import FlaskInterface
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest import config
from pdoauth.WebInterface import WebInterface
import uritools

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


    
    def test_authorization_code_cannot_be_obtained_without_user(self):
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

    
    def test_auth_interface_redirects_to_redirect_uri(self):
        params = {
            "response_type": "code",
            "client_id": self.app.name,
            "redirectUri": self.app.redirect_uri
        }
        baseUrl = app.config.get('BASE_URL')
        uriBase = "/v1/oauth2/auth"
        uri=WebInterface.parametrizeUri(baseUrl + uriBase, params)
        queryString=uri.split('?')[1].replace("%20"," ")
        with app.test_client() as client:
            resp = client.get(
                    uriBase, query_string=queryString, base_url=baseUrl)
            targetUri = WebInterface.parametrizeUri(
                app.config.get('LOGIN_URL'),
                {"next": uri}
            )
        targetUri = targetUri.replace("https://test.app/", "https:%252F%252Ftest.app%252F")
        targetUri = targetUri.replace("test%2520app%2520","test%20app%20")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'],targetUri)
