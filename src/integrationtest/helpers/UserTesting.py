#pylint: disable=no-member
from pdoauth.app import app, mail
from test.helpers.CryptoTestUtil import CryptoTestUtil
from test.helpers.RandomUtil import RandomUtil
from test.helpers.UserUtil import UserUtil
from test import config

app.extensions["mail"].suppress = True

class UserTesting(UserUtil, CryptoTestUtil, RandomUtil):

    def login(self, client):
        self.setupRandom()
        user = self.createUserWithCredentials().user
        self.userid = user.userid
        data = {
                'credentialType': 'password',
                'identifier': self.userCreationUserid,
                'secret': self.usercreationPassword
        }
        resp = client.post(config.BASE_URL+'/v1/login', data=data)
        return resp

    def prepareAuthInterfaceData(self, email=None):
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
            data = self.prepareAuthInterfaceData(email)
            resp = client.post(config.BASE_URL + '/v1/register', data=data)
            self.outbox = outbox
            return resp

    def prepareTokenInterfaceParameters(self, paramupdates, code):
        self.tokenParams['code'] = code
        self.tokenParams.update(paramupdates)
        for key, value in self.tokenParams.items():
            if value is None:
                del self.tokenParams[key]

    def callTokenInterface(self, paramupdates, code):
        self.prepareTokenInterfaceParameters(paramupdates, code)
        with app.test_client() as client:
            resp = client.post("/v1/oauth2/token", data=self.tokenParams)
        return resp
