from pdoauth.models.Credential import Credential
from pdoauth.FlaskInterface import FlaskInterface
from pdoauth.ReportedError import ReportedError
from test.helpers.FakeInterFace import FakeForm
from test.helpers.todeprecate.UserTesting import UserTesting
from test.helpers.PDUnitTest import PDUnitTest, test

class FacebookTest(PDUnitTest, UserTesting):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.user = self.createUserWithCredentials(credType="facebook")
        self.user.activate()
        self.controller.facebook_id = self.usercreation_userid
        self.controller.access_token = self.usercreation_password
        data = {
                'credentialType': 'facebook',
                'identifier': self.controller.facebook_id,
                'secret': self.controller.access_token
        }
        self.request_data = FakeForm(data)


    def tearDown(self):
        PDUnitTest.tearDown(self)

    @test
    def facebook_login_needs_facebook_id_and_access_token(self):
        resp = self.controller.do_login(self.request_data)
        self.assertEqual(resp.status_code, 200)

    @test
    def facebook_login_needs_facebook_id_as_username(self):
        self.request_data.set('identifier','badid')
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor,["bad facebook id"])

    @test
    def facebook_login_needs_correct_access_token_as_password(self):
        self.request_data.set('secret',self.mkRandomPassword())
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor, ["Cannot login to facebook"])

    @test
    def facebook_login_needs_facebook_credentials_as_registered(self):
        cred = Credential.getByUser(self.user, "facebook")
        cred.rm()
        with self.assertRaises(ReportedError) as e:
            self.controller.do_login(self.request_data)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor,["You have to register first"])

    @test
    def facebookMe_reaches_facebook(self):
        resp = FlaskInterface()._facebookMe("code")
        self.assertEqual(400, resp.status)
        self.assertTrue(resp.headers.has_key('x-fb-rev'))
        self.assertEqual('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}', resp.data)
        