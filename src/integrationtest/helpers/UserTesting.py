#pylint: disable=no-member
from pdoauth.app import app, mail
from test.helpers.CryptoTestUtil import CryptoTestUtil
from test.helpers.RandomUtil import RandomUtil
from test.helpers.UserUtil import UserUtil
from test import config
from pdoauth.forms import credErr

app.extensions["mail"].suppress = True

class UserTesting(UserUtil, CryptoTestUtil, RandomUtil):

    def login(self, client, user = None):
        if user is None:
            self.setupRandom()
            user = self.createUserWithCredentials().user
            self.userid = user.userid
            user.username = self.userCreationUserid
            user.password = self.usercreationPassword
        data = {
                'credentialType': 'password',
                'identifier': user.username,
                'password': user.password
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
            'password':self.registeredPassword,
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
        for key in list(self.tokenParams.keys()):
            if self.tokenParams[key] is None:
                del self.tokenParams[key]

    def callTokenInterface(self, paramupdates, code):
        self.prepareTokenInterfaceParameters(paramupdates, code)
        with app.test_client() as client:
            resp = client.post("/v1/oauth2/token", data=self.tokenParams)
        return resp

    def assertCredentialErrorresponse(self, resp):
        return self.assertEqual('{{"errors": [{0}]}}'.format(credErr), self.getResponseText(resp))

