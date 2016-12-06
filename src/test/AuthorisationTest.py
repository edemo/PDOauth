from pdoauth.Authorisation import Authorisation, OnlyEmptyScopeIsAllowed
import time
from pdoauth.app import app
from unittest.case import TestCase

EXPIRY = app.config.get('AUTHCODE_EXPIRY')

class AuthorisatonTest(TestCase):

    def setUp(self):
        self.authorisation_can_be_created_with_client_id__code_and_scope()

    def authorisation_can_be_created_with_client_id__code_and_scope(self):
        self.now = time.time()
        self.auth = Authorisation.new(
                    'client id', 'code', "", _called_at=self.now)

    
    def test_created_authorisation_can_be_retrieved_using_client_id_and_scope(self):
        self.assertEqual(self.auth, Authorisation.get('client id', 'code'))

    
    def test_created_authorisation_have_the_client_id_given(self):
        self.assertEqual(self.auth.client_id, 'client id')

    
    def test_created_authorisation_have_the_code_given(self):
        self.assertEqual(self.auth.code, 'code')

    
    def test_authorisation_should_have_empty_scope(self):
        self.assertRaises(
            OnlyEmptyScopeIsAllowed, Authorisation.new,
                'client id2', 'code2', "nonempty")

    
    def test_authorisation_code_expires_in_configured_time(self):
        authorization = Authorisation.get(
                            'client id', 'code', _called_at=self.now + EXPIRY)
        self.assertEqual(None, authorization)

    
    def test_authorisation_code_can_be_retrieved_before_configured_expiry(self):
        authorization = Authorisation.get(
                            'client id', 'code', _called_at=self.now + EXPIRY-1)
        self.assertEqual(self.auth, authorization)
