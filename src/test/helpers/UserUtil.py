from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Credential import Credential
from test.helpers.ResponseInfo import ResponseInfo
from test.helpers.RandomUtil import RandomUtil

class UserUtil(ResponseInfo, RandomUtil):
    def createUserWithCredentials(self, credType='password', userid=None, password=None, email=None):
        userid, password, email = self.setupUserCreationData(userid, password, email)
        user = CredentialManager.create_user_with_creds(credType, userid, password, email)
        self.assertTrue(user)
        return user
    
    def createLoggedInUser(self):
        self.setupRandom()
        user = self.createUserWithCredentials()
        user.activate()
        user.authenticated = True
        self.controller._testdata.current_user = user
        return user
    
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
