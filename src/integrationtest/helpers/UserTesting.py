#pylint: disable=no-member
from pdoauth.app import app, mail
from test.helpers.CryptoTestUtil import CryptoTestUtil
from test.helpers.RandomUtil import RandomUtil
from test.helpers.UserUtil import UserUtil
from pdoauth.models.User import User
from test import config
from pdoauth.models.Application import Application

app.extensions["mail"].suppress = True

class UserTesting(UserUtil, CryptoTestUtil, RandomUtil):

    def login(self, client, activate = True, createUser = True):
        self.setupRandom()
        if createUser:
            user = self.createUserWithCredentials().user
        else:
            user = User.getByEmail(self.userCreationEmail)
        if not activate:
            user.active = False
        self.userid = user.userid
        data = {
                'credentialType': 'password',
                'identifier': self.userCreationUserid,
                'secret': self.usercreationPassword
        }
        resp = client.post(config.BASE_URL+'/login', data=data)
        return resp

    def getCode(self, client):
        redirect_uri = 'https://test.app/redirecturi'
        appid = "app-{0}".format(self.randString)
        self.appsecret = "secret-{0}".format(self.randString)
        application = Application.new(appid, self.appsecret, redirect_uri)
        self.appid = application.appid
        uri = config.BASE_URL + '/v1/oauth2/auth'
        queryPattern = 'response_type=code&client_id={0}&redirect_uri={1}'
        queryString = queryPattern.format(self.appid, redirect_uri)
        resp = client.get(uri, query_string=queryString)
        self.assertEqual(302, resp.status_code)
        location = resp.headers['Location']
        urlStart = 'https://test.app/redirecturi?code='
        self.assertTrue(location.startswith(urlStart))
        return location.split('=')[1]

    def loginAndGetCode(self):
        with app.test_client() as client:
            self.login(client)
            return self.getCode(client)


    def prepareData(self, email=None):
        if email is None:
            email = "{0}@example.com".format(self.randString)
        self.registeredEmail = email
        self.registeredPassword = "password_{0}".format(self.mkRandomPassword())
        data = {'credentialType':'password',
            'identifier':"id_{0}".format(self.randString),
            'secret':self.registeredPassword,
            'email':email,
            'digest':self.createHash()}
        return data

    def register(self, client, email = None):
        with mail.record_messages() as outbox:
            data = self.prepareData(email)
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.outbox = outbox
            return resp
