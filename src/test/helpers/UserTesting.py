from pdoauth.app import app, mail
from test.helpers.CryptoTestUtil import CryptoTestUtil
from test.helpers.RandomUtil import RandomUtil
from test.helpers.UserUtil import UserUtil
from pdoauth.models.User import User
from test import config
from pdoauth.models.Application import Application
import pdoauth.main  # @UnusedImport

app.extensions["mail"].suppress = True

class UserTesting(UserUtil, CryptoTestUtil, RandomUtil):
    def login(self, c, activate = True, createUser = True):
        self.setupRandom()
        if createUser:
            user = self.createUserWithCredentials()
        else:
            user = User.getByEmail(self.usercreation_email)
        if activate:
            user.activate()
        data = {
                'credentialType': 'password',
                'identifier': self.usercreation_userid,
                'secret': self.usercreation_password
        }
        resp = c.post(config.base_url+'/login', data=data)
        return resp

    def getCode(self, c):
        redirect_uri = 'https://test.app/redirecturi'
        appid = "app-{0}".format(self.randString)
        self.appsecret = "secret-{0}".format(self.randString)
        application = Application.new(appid, self.appsecret, redirect_uri)
        self.appid = application.appid
        uri = config.base_url + '/v1/oauth2/auth'
        query_string = 'response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, 
            redirect_uri)
        resp = c.get(uri, query_string=query_string)
        self.assertEqual(302, resp.status_code)
        location = resp.headers['Location']
        self.assertTrue(location.startswith('https://test.app/redirecturi?code='))
        return location.split('=')[1]

    def loginAndGetCode(self):
        with app.test_client() as c:
            self.login(c)
            return self.getCode(c)

    def register(self, c, email = None):
        with mail.record_messages() as outbox:
            if email is None:
                email = "{0}@example.com".format(self.randString)
            self.registered_email = email
            self.registered_password = "password_{0}".format(self.mkRandomPassword())
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret': self.registered_password,
                'email': email, 
                'digest': self.createHash()
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            return resp, outbox
