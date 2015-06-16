from twatson.unittest_annotations import Fixture, test

from pdoauth.Authorisation import Authorisation, OnlyEmptyScopeIsAllowed
import time
from pdoauth.app import app

EXPIRY = app.config.get('AUTHCODE_EXPIRY')

class AuthorisatonTest(Fixture):

    def setUp(self):
        self.authorisation_can_be_created_with_client_id__code_and_scope()

    def authorisation_can_be_created_with_client_id__code_and_scope(self):
        self.now = time.time()
        self.auth = Authorisation.new(
                    'client id', 'code', "", _called_at=self.now)

    @test
    def created_authorisation_can_be_retrieved_using_client_id_and_scope(self):
        self.assertEquals(self.auth, Authorisation.get('client id', 'code'))

    @test
    def created_authorisation_have_the_client_id_given(self):
        self.assertEquals(self.auth.client_id, 'client id')

    @test
    def created_authorisation_have_the_code_given(self):
        self.assertEquals(self.auth.code, 'code')

    @test
    def authorisation_should_have_empty_scope(self):
        self.assertRaises(
            OnlyEmptyScopeIsAllowed, Authorisation.new,
                'client id2', 'code2', "nonempty")

    @test
    def authorisation_code_expires_in_configured_time(self):
        authorization = Authorisation.get(
                            'client id', 'code', _called_at=self.now + EXPIRY)
        self.assertEqual(None, authorization)

    @test
    def authorisation_code_can_be_retrieved_before_configured_expiry(self):
        authorization = Authorisation.get(
                            'client id', 'code', _called_at=self.now + EXPIRY-1)
        self.assertEqual(self.auth, authorization)
