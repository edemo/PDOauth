from twatson.unittest_annotations import Fixture, test
from pdoauth.models.Credential import Credential
from pdoauth.models import User

class CredentialTest(Fixture):
    def setUp(self):
        Credential.query.delete()  # @UndefinedVariable
        User.query.delete()  # @UndefinedVariable
        self.Credential_can_be_created_with_user__credential_type__identifier_and_secret()
        
    def Credential_can_be_created_with_user__credential_type__identifier_and_secret(self):
        self.user = User.new("emailtest@example.com")
        self.cred = Credential.new(self.user,'password','username','password')
        self.assertEquals("{0}".format(self.cred),"Credential(user=emailtest@example.com,credentialType=password,secret=password)")
        
    @test
    def Credential_can_be_retrieved_by_type_and_identifier(self):
        cred = Credential.get('password', 'username')
        self.assertEquals(cred, self.cred)
        self.assertEquals(False, self.user.is_active())
        self.assertEquals(False, self.user.is_authenticated())
        self.assertEquals(False, cred.user.is_active())
        self.assertEquals(False, cred.user.is_authenticated())
