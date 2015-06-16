from pdoauth.models.Credential import Credential
from pdoauth.FlaskInterface import FlaskInterface
from pdoauth.ReportedError import ReportedError
from test.helpers.FakeInterFace import FakeForm
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil

class FacebookTest(PDUnitTest, UserUtil):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.cred = self.createUserWithCredentials(credType="facebook")
        self.cred.user.activate()
        interface = self.controller.interface
        interface.facebook_id = self.userCreationUserid
        interface.accessToken = self.usercreationPassword
        data = {
                'credentialType': 'facebook',
                'identifier': interface.facebook_id,
                'secret': interface.accessToken
        }
        self.form = FakeForm(data)


    def tearDown(self):
        PDUnitTest.tearDown(self)

    @test
    def facebook_login_needs_facebook_id_and_access_token(self):
        resp = self.controller.doLogin(self.form)
        self.assertEqual(resp.status_code, 200)

    @test
    def facebook_login_needs_facebook_id_as_username(self):
        form = self.form
        form.set('identifier','badid')
        with self.assertRaises(ReportedError) as e:
            self.controller.doLogin(form)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor,["bad facebook id"])

    @test
    def facebook_login_needs_correct_access_token_as_password(self):
        self.form.set('secret',self.mkRandomPassword())
        with self.assertRaises(ReportedError) as e:
            self.controller.doLogin(self.form)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor, ["Cannot login to facebook"])

    @test
    def facebook_login_needs_facebook_credentials_as_registered(self):
        self.cred.rm()
        with self.assertRaises(ReportedError) as e:
            self.controller.doLogin(self.form)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(e.exception.descriptor,["You have to register first"])

    @test
    def facebookMe_reaches_facebook(self):
        resp = FlaskInterface().facebookMe("code")
        self.assertEqual(400, resp.status)
        self.assertTrue(resp.headers.has_key('x-fb-rev'))
        self.assertEqual('{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}', resp.data)
