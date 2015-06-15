from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Credential import Credential
from Crypto.Hash.SHA256 import SHA256Hash
from test.helpers.CryptoTestUtil import CryptoTestUtil
from pdoauth.models.Assurance import Assurance

class RegistrationTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def _prepareTest(self, digest =None, email=None):
        self.setupUserCreationData()
        self.data = dict(credentialType='password',
                identifier=self.usercreation_userid,
                secret=self.usercreation_password,
                email=None,
                digest=None)
        self.addDataBasedOnOptionValue('email', email, self.usercreation_email)
        self.addDataBasedOnOptionValue('digest', digest, self.createHash())
        form = FakeForm(self.data)
        return form

    @test
    def password_is_stored_hashed_in_registration(self):
        form = self._prepareTest()
        self.controller.do_registration(form)
        cred = Credential.get('password', self.usercreation_userid)
        self.assertEqual(cred.secret, SHA256Hash(self.usercreation_password).hexdigest())

    @test
    def on_registration_a_temporary_email_verification_credential_is_registered(self):
        form = self._prepareTest()
        self.controller.do_registration(form)
        cred = Credential.getByUser(self.controller.getCurrentUser(), 'emailcheck')
        self.assertTrue(cred)

    @test
    def the_emailcheck_secret_is_not_shown_in_the_registration_answer(self):
        form = self._prepareTest()
        resp = self.controller.do_registration(form)
        text = self.getResponseText(resp)
        cred = Credential.getByUser(self.controller.getCurrentUser(), 'emailcheck')
        self.assertTrue(not (cred.secret in text))

    @test
    def you_can_register_without_hash(self):
        form = self._prepareTest(digest=False)
        self.controller.do_registration(form)
        self.assertEqual(self.controller.getCurrentUser().hash, None)

    @test
    def you_are_logged_in_in_registration(self):
        form = self._prepareTest()
        self.controller.do_registration(form)
        self.assertEqual(self.controller.getCurrentUser().email,
            self.usercreation_email)

    def _registerAndGetEmail(self):
        form = self._prepareTest()
        self.controller.do_registration(form)
        msg = self.controller.mail.outbox[0]['body']
        return msg

    @test
    def registration_sends_registration_email(self):
        msg = self._registerAndGetEmail()
        self.assertTrue(msg)

    @test
    def registration_email_contains_registration_uri_with_secret(self):
        msg = self._registerAndGetEmail()
        self.assertTrue(msg)
        cred = Credential.getByUser(self.controller.getCurrentUser(), 'emailcheck')
        uri = "{0}/v1/verify_email/{1}".format(self.controller.getConfig('BASE_URL'),cred.secret)
        self.assertTrue(uri in msg)

    @test
    def user_cannot_register_twice_with_same_email(self):
        self.setupRandom()
        email = "k-{0}@example.com".format(self.randString)
        form = self._prepareTest(email=email)
        self.controller.do_registration(form)
        form = self._prepareTest(email=email)
        self.assertReportedError(self.controller.do_registration, [form], 400, ["there is already a user with this email"])

    @test
    def When_a_hash_is_registered_which_is_already_used_by_another_user___the_user_is_notified_about_the_fact(self):
        theHash = self.createHash()
        form = self._prepareTest(digest=theHash)
        anotherUser = self.createUserWithCredentials().user
        anotherUser.hash = theHash
        resp = self.controller.do_registration(form)
        self.assertEqual(200, resp.status_code)
        data = self.fromJson(resp)
        self.assertEqual(data['message'],"another user is using your hash")

    @test
    def When_a_hash_is_registered_which_is_already_used_by_another_assured_user___the_user_is_notified_about_the_fact_and_registration_fails(self):
        anotherUser = self.createUserWithCredentials().user
        Assurance.new(anotherUser, "test", anotherUser)
        theHash = self.createHash()
        anotherUser.hash = theHash
        form = self._prepareTest(digest=theHash)
        self.assertReportedError(self.controller.do_registration, [form], 400, ['another user is using your hash'])

    @test
    def the_emailverification_assurance_does_not_count_in_hash_collision(self):
        anotherUser = self.createUserWithCredentials().user
        Assurance.new(anotherUser, "emailverification", anotherUser)
        theHash = self.createHash()
        anotherUser.hash = theHash
        form = self._prepareTest(digest=theHash)
        resp = self.controller.do_registration(form)
        self.assertEqual(200, resp.status_code)
        data = self.fromJson(resp)
        self.assertEqual(data['message'],"another user is using your hash")
