from pdoauth.Controller import FlaskInterface, Controller
from flask import json
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from test.TestUtil import UserTesting
from pdoauth.models.Credential import Credential


class record(object):
    pass

class FakeInterface(FlaskInterface):
    
    def validate_on_submit(self,form):
        for k in self.request_data.keys():
            getattr(form,k).data = self.request_data[k]
        return form.validate()

    def _facebookMe(self, code):
        resp = record()
        if self.access_token == code:
            resp.status = 200
            resp.data = json.dumps(dict(id=self.facebook_id))
        else:
            resp.status = 404
        return resp


class FacebookTest(Fixture, UserTesting):
    def setUp(self):
        self.controller = Controller(FakeInterface)
        self.user = self.createUserWithCredentials(credType="facebook")
        self.user.activate()
        self.controller.facebook_id = self.usercreation_userid
        self.controller.access_token = self.usercreation_password
        data = {
                'credentialType': 'facebook',
                'identifier': self.controller.facebook_id,
                'secret': self.controller.access_token
        }
        self.controller.request_data = data

    @test
    def facebook_login_needs_facebook_id_and_access_token(self):
        with app.test_request_context():
            resp = self.controller.do_login()
            self.assertEqual(resp.status_code, 200)

    @test
    def facebook_login_needs_facebook_id_as_username(self):
        self.controller.request_data['identifier'] = 'badid'
        with app.test_request_context():
            resp = self.controller.do_login()
            self.assertEqual(resp.status_code, 403)
            data = self.fromJson(resp)
            self.assertEqual(data['errors'],["bad facebook id"])

    @test
    def facebook_login_needs_correct_access_token_as_password(self):
        self.controller.request_data['secret'] = self.mkRandomPassword()
        with app.test_request_context():
            resp = self.controller.do_login()
            self.assertEqual(resp.status_code, 403)
            data = self.fromJson(resp)
            self.assertEqual(data['errors'],["Cannot login to facebook"])

    @test
    def facebook_login_needs_facebook_credentials_as_registered(self):
        cred = Credential.getByUser(self.user, "facebook")
        cred.rm()
        with app.test_request_context():
            resp = self.controller.do_login()
            self.assertEqual(resp.status_code, 403)
            data = self.fromJson(resp)
            self.assertEqual(data['errors'],["You have to register first"])
