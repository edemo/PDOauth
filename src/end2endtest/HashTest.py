from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
import config

class HashTest(Fixture,BrowsingUtil):

    @test
    def you_can_obtain_the_hash_by_filling_in_your_personal_id_and_pushing_the_button_near_it(self):
        """
        In this case your web browser goes directly to anchor.edemokraciagep.org, and gets the hash for you.
        The SSO server never sees your personal id.
        """
        self.goToLoginPage()
        self.switchToTab('registration')
        self.obtainHash("11111111110", "Mother Test", "RegistrationForm")
        self.assertHashFromFormEquals("RegistrationForm", config.testSignatureAllOne)

    @test
    def assurer_can_obtain_the_hash_by_filling_in_your_personal_id__mother_name_and_pushing_the_button_near_it(self):
        self.loginWithPasswordAs(TE.assurerUser)
        self.switchToTab("assurer")
        self.obtainHash("22222222220", "Test Mother", "AddAssuranceForm")
        self.assertHashFromFormEquals("AddAssuranceForm", config.testSignatureAllTwo)

    def tearDown(self):
        BrowsingUtil.tearDown(self)