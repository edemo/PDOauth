from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Credential import Credential
from test.helpers.ResponseInfo import ResponseInfo
from test.helpers.RandomUtil import RandomUtil

class UserUtil(ResponseInfo, RandomUtil):

    def addDataBasedOnOptionValue(self, name, optval, default):
        if optval is not False:
            if optval is None:
                token = default
            else:
                token = optval
            self.data[name] = token

    def getCookieParts(self, response):
        cookieHeader = response.headers['Set-Cookie']
        cookieparts = cookieHeader.split(';')
        cookieDict = dict()
        for part in cookieparts:
            key,value = part.split("=")
            cookieDict[key.strip()] = value.strip()
        return cookieDict

    def createUserWithCredentials(self, credType='password', userid=None, password=None, email=None):
        userid, password, email = self.setupUserCreationData(userid, password, email)
        cred = CredentialManager.create_user_with_creds(credType, userid, password, email)
        cred.user.activate()
        return cred
    
    def createLoggedInUser(self):
        self.setupRandom()
        self.cred = self.createUserWithCredentials()
        self.cred.user.authenticated = True
        self.controller.loginInFramework(self.cred)
        return self.cred
    
    def deleteUser(self, user):
        for cred in Credential.getByUser(user):
            cred.rm()
        
        user.rm()

    def assertUserResponse(self, resp):
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertEquals(data['assurances'], {})
        self.assertTrue("@example.com" in data['email'])
        self.assertTrue(data.has_key('userid'))
        return data

    def showUserByCurrentUser(self, userid):
        self.controller.getSession()['auth_user'] =  (self.controller.getCurrentUser().userid, True)
        resp = self.controller.do_show_user(userid=userid)
        return resp
