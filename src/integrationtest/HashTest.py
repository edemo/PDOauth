from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from pdoauth.app import app
from integrationtest import config
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance, emailVerification
import time
from integrationtest.helpers.CSRFMixin import CSRFMixin
from integrationtest.helpers.UserTesting import UserTesting

class HashTest(IntegrationTest, UserTesting, CSRFMixin):

    @test
    def a_logged_in_user_can_record_its_hash(self):
        with app.test_client() as client:
            resp = self.login(client)
            csrf = self.getCSRF(client)
            self.assertUserResponse(resp)

            data = dict(
                digest= self.createHash(),
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            self.assertEqual('{"message": "new hash registered"}', self.getResponseText(resp))

    @test
    def the_users_hash_is_changed_to_the_new_one(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            user = User.getByEmail(self.userCreationEmail)
            self.assertEqual(user.hash, None)
            digest = self.createHash()
            csrf = self.getCSRF(client)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.userCreationEmail)
            self.assertEqual(userAfter.hash, digest)

    @test
    def if_the_user_had_a_hash_before__it_is_overwritten(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            user = User.getByEmail(self.userCreationEmail)
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.userCreationEmail)
            self.assertEqual(userToCheck.hash, oldHash)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(client)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.userCreationEmail)
            self.assertEqual(userAfter.hash, digest)

    @test
    def it_is_possible_to_delete_the_hash_by_not_giving_a_digest_in_the_request(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            user = User.getByEmail(self.userCreationEmail)
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.userCreationEmail)
            self.assertEqual(userToCheck.hash, oldHash)
            self.setupRandom()
            csrf = self.getCSRF(client)
            data = dict(
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.userCreationEmail)
            self.assertEqual(userAfter.hash, None)

    @test
    def the_assurances_are_overwritten_on_hash_update(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            user = User.getByEmail(self.userCreationEmail)
            Assurance.new(user, "test", user, time.time())
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.userCreationEmail)
            self.assertEqual(len(Assurance.getByUser(userToCheck)), 1)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(client)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.userCreationEmail)
            self.assertEqual(len(Assurance.getByUser(userAfter)), 0)

    @test
    def emailverification_assurance_is_an_exception_from_overwriting(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            user = User.getByEmail(self.userCreationEmail)
            Assurance.new(user, emailVerification, user, time.time())
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.userCreationEmail)
            self.assertEqual(len(Assurance.getByUser(userToCheck)), 1)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(client)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.userCreationEmail)
            self.assertEqual(len(Assurance.getByUser(userAfter)), 1)

    @test
    def without_login_it_is_not_possible_to_update_the_hash(self):
        self.setupRandom()
        with app.test_client() as client:
            csrf = self.getCSRF(client)
            data = dict(
                digest= self.createHash(),
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(403,resp.status_code)

    @test
    def the_hash_update_request_should_contain_csrf_token(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)

            data = dict(
                digest= self.createHash(),
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(400,resp.status_code)
            self.assertEqual(
                '{"errors": ["csrf_token: csrf validation error"]}'
                ,self.getResponseText(resp)
            )

    @test
    def if_a_hash_is_given_it_should_be_valid(self):
        with app.test_client() as client:
            resp = self.login(client)
            self.assertUserResponse(resp)
            csrf = self.getCSRF(client)
            data = dict(
                digest= 'invalidhash',
                csrf_token= csrf
            )
            resp = client.post(config.BASE_URL+'/v1/users/me/update_hash', data=data)
            self.assertEqual(400,resp.status_code)
            self.assertEqual(
                '{"errors": ["digest: Field must be between 128 and 128 characters long."]}'
                ,self.getResponseText(resp)
            )

