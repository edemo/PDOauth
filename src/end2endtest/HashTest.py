#coding=UTF-8
from twatson.unittest_annotations import Fixture, test
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
import config
from selenium.webdriver.common.by import By
import time

class HashTest(Fixture,BrowsingUtil):

    def giveHash(self):
        self.goToLoginPage()
        self.switchToTab('register')
        self.click("create_here")
        self.obtainHash("11111111110", "Mother Test", "registration-form")
        self.assertHashFromFormEquals("registration-form", config.testSignatureAllOne)

    @test
    def you_can_obtain_the_hash_by_filling_in_your_personal_id_and_pushing_the_button_near_it(self):
        """
        In this case your web browser goes directly to anchor.edemokraciagep.org, and gets the hash for you.
        The SSO server never sees your personal id.
        """
        self.giveHash()

    @test
    def if_you_give_hash_in_registration_you_will_have_a_hashgiven_assurance(self):
        self.goToLoginPage()
        self.switchToTab('register')
        mothername=self.createRandomUserId()
        self.registerUser(personalId="11111111110", motherName=mothername)
        self.assertPopupErrorMatchesRe("emailben megadott")
        self.closeMessage()
        self.assertElementMatchesRe("me_Data", "van Titkos K\xf3d")

    @test
    def if_you_give_hash_after_registration_you_will_have_a_hashgiven_assurance(self):
        self.goToLoginPage()
        self.switchToTab('register')
        mothername=self.createRandomUserId()
        self.registerUser()
        self.assertPopupErrorMatchesRe("emailben megadott")
        self.closeMessage()
        time.sleep(1)
        self.switchToSection("settings")
        self.click("viewChangeHashForm")
        self.click("create_hash_here")
        self.obtainHash("11111111110", mothername, "change-hash-form")
        self.click("changeHash")
        self.assertElementMatchesRe("change-hash-form_digest-pre", "[0-9a-f]{10}")
        time.sleep(2)
        self.switchToSection("account")
        time.sleep(2)
        self.assertElementMatchesRe("me_Data", "van Titkos K\xf3d")

    @test
    def assurer_can_obtain_the_hash_by_filling_in_your_personal_id__mother_name_and_pushing_the_button_near_it(self):
        self.loginWithPasswordAs(TE.assurerUser)
        self.switchToSection("assurer")
        self.obtainHash("22222222220", "Test Mother", "assurancing")
        self.wait_on_element_class(By.ID, 'assurance-giving_message', "given")

    def tearDown(self):
        BrowsingUtil.tearDown(self)