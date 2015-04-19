from twatson.unittest_annotations import Fixture, test

from pdoauth.Authorisation import Authorisation, OnlyEmptyScopeIsAllowed
import time
from pdoauth.app import app

expiry = app.config.get('AUTHCODE_EXPIRY')

class AuthorisatonTest(Fixture):

    def setUp(self):
        self.Authorisation_can_be_created_with_client_id__code_and_scope()

    def Authorisation_can_be_created_with_client_id__code_and_scope(self):
        self.now = time.time()
        self.auth = Authorisation.new('client id', 'code', "", _called_at=self.now)
        
    @test
    def Created_authorisation_can_be_retrieved_using_client_id_and_scope(self):
        self.assertEquals(self.auth, Authorisation.get('client id', 'code'))

    @test
    def Created_authorisation_have_the_client_id_given(self):
        self.assertEquals(self.auth.client_id, 'client id')
    
    @test
    def Created_authorisation_have_the_code_given(self):
        self.assertEquals(self.auth.code, 'code')

    @test
    def Authorisation_should_have_empty_scope(self):
        self.assertRaises(OnlyEmptyScopeIsAllowed, Authorisation.new,'client id2', 'code2', "nonempty")
        
    @test
    def Authorisation_code_expires_in_configured_time(self):
        self.assertEqual(None, Authorisation.get('client id', 'code', _called_at = self.now + expiry))

    @test
    def Authorisation_code_can_be_retrieved_before_configured_expiry(self):
        self.assertEqual(self.auth, Authorisation.get('client id', 'code', _called_at = self.now+ expiry - 1))
