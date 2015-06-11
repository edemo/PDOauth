from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
import config
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance, emailVerification
import time
from test.helpers.CSRFMixin import CSRFMixin
from test.helpers.todeprecate.UserTesting import UserTesting


class HashTest(Fixture, UserTesting, CSRFMixin):

    @test
    def a_logged_in_user_can_record_its_hash(self):
        with app.test_client() as c:
            resp = self.login(c)
            csrf = self.getCSRF(c)
            self.assertUserResponse(resp)
            
            data = dict(
                digest= self.createHash(),
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            self.assertEqual('{"message": "new hash registered"}', self.getResponseText(resp))

    @test
    def the_users_hash_is_changed_to_the_new_one(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            user = User.getByEmail(self.usercreation_email)
            self.assertEqual(user.hash, None)
            digest = self.createHash()
            csrf = self.getCSRF(c)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.usercreation_email)
            self.assertEqual(userAfter.hash, digest)

    @test
    def if_the_user_had_a_hash_before__it_is_overwritten(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            user = User.getByEmail(self.usercreation_email)
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.usercreation_email)
            self.assertEqual(userToCheck.hash, oldHash)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(c)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.usercreation_email)
            self.assertEqual(userAfter.hash, digest)

    @test
    def it_is_possible_to_delete_the_hash_by_not_giving_a_digest_in_the_request(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            user = User.getByEmail(self.usercreation_email)
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.usercreation_email)
            self.assertEqual(userToCheck.hash, oldHash)
            self.setupRandom()
            csrf = self.getCSRF(c)
            data = dict(
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.usercreation_email)
            self.assertEqual(userAfter.hash, None)
            
    @test
    def the_assurances_are_overwritten_on_hash_update(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            user = User.getByEmail(self.usercreation_email)
            Assurance.new(user, "test", user, time.time())
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.usercreation_email)
            self.assertEqual(len(Assurance.getByUser(userToCheck)), 1)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(c)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.usercreation_email)
            self.assertEqual(len(Assurance.getByUser(userAfter)), 0)

    @test
    def emailverification_assurance_is_an_exception_from_overwriting(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            user = User.getByEmail(self.usercreation_email)
            Assurance.new(user, emailVerification, user, time.time())
            oldHash = self.createHash()
            user.hash = oldHash
            userToCheck = User.getByEmail(self.usercreation_email)
            self.assertEqual(len(Assurance.getByUser(userToCheck)), 1)
            self.setupRandom()
            digest = oldHash
            csrf = self.getCSRF(c)
            data = dict(
                digest= digest,
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(200,resp.status_code)
            userAfter = User.getByEmail(self.usercreation_email)
            self.assertEqual(len(Assurance.getByUser(userAfter)), 1)

    @test
    def without_login_it_is_not_possible_to_update_the_hash(self):
        self.setupRandom()
        with app.test_client() as c:
            csrf = self.getCSRF(c)
            data = dict(
                digest= self.createHash(),
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(403,resp.status_code)

    @test
    def the_hash_update_request_should_contain_csrf_token(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            
            data = dict(
                digest= self.createHash(),
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(400,resp.status_code)
            self.assertEqual(
                '{"errors": ["csrf_token: csrf validation error"]}'
                ,self.getResponseText(resp)
            )

    @test
    def if_a_hash_is_given_it_should_be_valid(self):
        with app.test_client() as c:
            resp = self.login(c)
            self.assertUserResponse(resp)
            csrf = self.getCSRF(c)            
            data = dict(
                digest= 'invalidhash',
                csrf_token= csrf
            )
            resp = c.post(config.base_url+'/v1/users/me/update_hash', data=data)
            self.assertEqual(400,resp.status_code)
            self.assertEqual(
                '{"errors": ["digest: Field must be between 512 and 512 characters long."]}'
                ,self.getResponseText(resp)
            )

