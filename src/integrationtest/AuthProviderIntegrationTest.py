# -*- coding: UTF-8 -*-
# pylint: disable=no-member, invalid-name
from integrationtest.helpers.IntegrationTest import IntegrationTest
from pdoauth.AuthProvider import AuthProvider
from pdoauth.models.Application import Application
from pdoauth.app import db, app
from pdoauth.FlaskInterface import FlaskInterface
from integrationtest.helpers.UserTesting import UserTesting
from integrationtest import config
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
        baseUrl = app.config.get('BASE_URL')
        uriBase = "/v1/oauth2/auth"
        uri="{0}{1}?redirectUri={2}&response_type=code&client_id={3}".format(
            baseUrl,
            uriBase,
            uritools.uriencode(self.app.redirect_uri).decode('utf-8'),
            self.app.name,
            )
        targetUri = "{0}?next={1}".format(app.config.get('LOGIN_URL'), uritools.uriencode(uri).decode('utf-8'))
        queryString=uri.split('?')[1]
        with app.test_client() as client:
            resp = client.get(
                    uriBase, query_string=queryString, base_url=baseUrl)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'],targetUri)
