# pylint: disable=line-too-long
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeForm
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Credential import Credential
from Crypto.Hash.SHA256 import SHA256Hash
from test.helpers.CryptoTestUtil import CryptoTestUtil, SPKAC
from pdoauth.models.Assurance import Assurance

class RegistrationTest(PDUnitTest, UserUtil, CryptoTestUtil):

    def prepareLoginForm(self, digest =None, email=None):
        self.setupUserCreationData()
        self.data = dict(credentialType='password',
                identifier=self.userCreationUserid,
                secret=self.usercreationPassword,
                email=None,
                digest=None)
        self.addDataBasedOnOptionValue('email', email, self.userCreationEmail)
        self.addDataBasedOnOptionValue('digest', digest, self.createHash())
        form = FakeForm(self.data)
        return form

    @test
    def password_is_stored_hashed_in_registration(self):
        form = self.prepareLoginForm()
        self.controller.doRegistration(form)
        cred = Credential.get('password', self.userCreationUserid)
        theSecret = SHA256Hash(self.usercreationPassword).hexdigest()
        self.assertEqual(cred.secret, theSecret)

    @test
    def on_registration_a_temporary_email_verification_credential_is_registered(self):
        form = self.prepareLoginForm()
        self.controller.doRegistration(form)
        current_user = self.controller.getCurrentUser()
        cred = Credential.getByUser(current_user, 'emailcheck')
        self.assertTrue(cred)

    @test
    def the_emailcheck_secret_is_not_shown_in_the_registration_answer(self):
        form = self.prepareLoginForm()
        resp = self.controller.doRegistration(form)
        text = self.getResponseText(resp)
        current_user = self.controller.getCurrentUser()
        cred = Credential.getByUser(current_user, 'emailcheck')
        self.assertTrue(not cred.secret in text)

    @test
    def you_can_register_without_hash(self):
        form = self.prepareLoginForm(digest=False)
        self.controller.doRegistration(form)
        self.assertEqual(self.controller.getCurrentUser().hash, None)

    @test
    def you_are_logged_in_in_registration(self):
        form = self.prepareLoginForm()
        self.controller.doRegistration(form)
        self.assertEqual(self.controller.getCurrentUser().email,
            self.userCreationEmail)

    def _registerAndGetEmail(self):
        form = self.prepareLoginForm()
        self.controller.doRegistration(form)
        msg = self.controller.mail.outbox[0]
        return msg

    @test
    def registration_sends_registration_email(self):
        msg = self._registerAndGetEmail()
        self.assertTrue(msg)

    @test
    def registration_email_contains_registration_uri_with_secret(self):
        msg = self._registerAndGetEmail()
        self.assertTrue(msg)
        current_user = self.controller.getCurrentUser()
        cred = Credential.getByUser(current_user, 'emailcheck')
        base_url = self.controller.getConfig('BASE_URL')
        uri = "{0}/v1/verify_email/{1}".format(base_url,cred.secret)
        self.assertEmailContains(uri, msg)

    @test
    def user_cannot_register_twice_with_same_email_address(self):
        self.setupRandom()
        email = "k-{0}@example.com".format(self.randString)
        form = self.prepareLoginForm(email=email)
        self.controller.doRegistration(form)
        form = self.prepareLoginForm(email=email)
        self.assertReportedError(
            self.controller.doRegistration,
            [form],
            400,
            ["there is already a user with this email"])

    @test
    def when_a_hash_is_registered_which_is_already_used_by_another_user___the_user_is_notified_about_the_fact(self):
        theHash = self.createHash()
        form = self.prepareLoginForm(digest=theHash)
        anotherUser = self.createUserWithCredentials().user
        anotherUser.hash = theHash
        resp = self.controller.doRegistration(form)
        self.assertEqual(200, resp.status_code)
        data = self.fromJson(resp)
        self.assertEqual(data['message'],"another user is using your hash")

    @test
    def when_a_hash_is_registered_which_is_already_used_by_another_assured_user___the_user_is_notified_about_the_fact_and_registration_fails(self):
        anotherUser = self.createUserWithCredentials().user
        Assurance.new(anotherUser, "test", anotherUser)
        theHash = self.createHash()
        anotherUser.hash = theHash
        form = self.prepareLoginForm(digest=theHash)
        self.assertReportedError(self.controller.doRegistration,
            [form],
            400,
            ['another user is using your hash'])

    @test
    def the_emailverification_assurance_does_not_count_in_hash_collision(self):
        anotherUser = self.createUserWithCredentials().user
        Assurance.new(anotherUser, "emailverification", anotherUser)
        theHash = self.createHash()
        anotherUser.hash = theHash
        form = self.prepareLoginForm(digest=theHash)
        resp = self.controller.doRegistration(form)
        self.assertEqual(200, resp.status_code)
        data = self.fromJson(resp)
        self.assertEqual(data['message'],"another user is using your hash")

    def _sslRegister(self):
        self.setupUserCreationData()
        data = dict(email=self.userCreationEmail, pubkey=SPKAC)
        resp = self.controller.doKeygen(FakeForm(data))
        return resp

    @test
    def you_can_register_with_a_generated_certificate_via_keygen(self):
        self._sslRegister()
        self.assertTrue(self.controller.getCurrentUser().email, self.userCreationEmail)

    @test
    def registration_sets_the_csrf_cookie(self):
        form = self.prepareLoginForm()
        resp = self.controller.doRegistration(form)
        self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))

    @test
    def ssl_registration_sets_the_csrf_cookie(self):
        resp = self._sslRegister()
        self.assertTrue("csrf=" in unicode(resp.headers['Set-Cookie']))
