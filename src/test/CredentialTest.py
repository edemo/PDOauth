from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.Credential import Credential
from test.helpers.UserUtil import UserUtil

class CredentialTest(PDUnitTest, UserUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials()
        self.cred=Credential.get('password', self.usercreation_userid)
        PDUnitTest.setUp(self)
        
    def tearDown(self):
        session = self.controller.getSession()
        if session.has_key(self.controller.LOGIN_CREDENTIAL_ATTRIBUTE):
            del(session[self.controller.LOGIN_CREDENTIAL_ATTRIBUTE])
        PDUnitTest.tearDown(self)
    
    @test
    def credential_removal_is_resistant_to_no_login_credential_in_session(self):
        form = FakeForm(dict(credentialType='password', identifier=self.usercreation_userid))
        self.assertReportedError(self.controller.do_remove_credential, [form], 500, ["Internal error: no login credential found"])

    @test
    def Credential_representation_is_readable(self):
        secretdigest=SHA256Hash(self.usercreation_password).hexdigest()
        representation = "Credential(user={0},credentialType=password,secret={1})".format(
            self.usercreation_email,
            secretdigest)
        self.assertEquals("{0}".format(self.cred),representation)

    @test
    def a_logged_in_user_can_add_credential(self):
        resp = self.createPasswordCredential()
        self.assertEqual(resp.status_code, 200)

    @test
    def when_a_credential_is_added_the_response_contains_user_data_which_contains_her_credentials(self):
        resp = self.createPasswordCredential()
        self.assertEqual(resp.status_code, 200)
        text = self.getResponseText(resp)
        self.assertTrue(self.usercreation_userid in text)

    @test
    def the_credential_is_actually_added(self):
        myUserid = self.createRandomUserId()
        credBefore = Credential.get("password", myUserid)
        self.assertTrue(credBefore is None)
        resp = self.createPasswordCredential(userid=myUserid)
        self.assertEqual(200, resp.status_code)
        credAfter = Credential.get("password", myUserid)
        self.assertTrue(credAfter is not None)

    @test
    def a_credential_can_be_deleted(self):
        myUserid = self.createRandomUserId()
        resp = self.removeACredential(myUserid)
        self.assertEqual(200, resp.status_code)
        self.assertEqual('{"message": "credential removed"}', self.getResponseText(resp))

    def loginACredential(self, cred):
        self.controller.setLoginCredentialIntoSession(cred.credentialType, cred.identifier)
        self.controller.loginUserInFramework(cred.user)

    def removeACredential(self, myUserid):
        self.loginACredential(self.cred)
        user = self.cred.user
        Credential.new(user, "facebook", myUserid, "testsecret")
        data = {"credentialType":"facebook", 
            "identifier":myUserid}
        self.assertTrue(Credential.get("facebook", myUserid))
        resp = self.controller.do_remove_credential(FakeForm(data))
        return resp

    def createPasswordCredential(self, userid=None):
        self.controller.loginUserInFramework(self.cred.user)
        self.setupUserCreationData()
        if userid is None:
            userid = self.usercreation_userid
        form = FakeForm(dict(credentialType='password', identifier=userid, secret=self.usercreation_password))
        resp = self.controller.do_add_credential(form)
        return resp

