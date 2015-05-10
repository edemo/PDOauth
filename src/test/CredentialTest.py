from twatson.unittest_annotations import Fixture, test
from pdoauth.models.Credential import Credential
from test.TestUtil import UserTesting
from Crypto.Hash.SHA256 import SHA256Hash

class CredentialTest(Fixture, UserTesting):
    def setUp(self):
        self.setupRandom()
        self.user = self.create_user_with_credentials()
        self.cred=Credential.get('password', self.usercreation_userid)

    @test
    def Credential_representation_is_readable(self):
        secretdigest=SHA256Hash(self.usercreation_password).hexdigest()
        representation = "Credential(user={0},credentialType=password,secret={1})".format(
            self.usercreation_email,
            secretdigest)
        self.assertEquals("{0}".format(self.cred),representation)
        
    @test
    def Credential_can_be_retrieved_by_type_and_identifier(self):
        self.assertEquals(self.cred.user, self.user)
