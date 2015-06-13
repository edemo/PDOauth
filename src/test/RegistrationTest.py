from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Credential import Credential
from Crypto.Hash.SHA256 import SHA256Hash

class RegistrationTest(PDUnitTest, UserUtil):
    
    @test
    def password_is_stored_hashed_in_registration(self):
        self.setupUserCreationData()
        form = FakeForm(dict(
                credentialType = 'password',
                identifier=self.usercreation_userid,
                secret = self.usercreation_password,
                email = self.usercreation_email,
                digest = None
            ))
        self.controller.do_registration(form)
        cred = Credential.get('password', self.usercreation_userid)
        self.assertEqual(cred.secret, SHA256Hash(self.usercreation_password).hexdigest())
