#coding=UTF-8
from end2endtest.helpers.BrowsingUtil import BrowsingUtil, TE
import config
from selenium.webdriver.common.by import By
import time
from pdoauth.models import Assurance
from test.helpers.UserUtil import UserUtil
from test.helpers.CryptoTestUtil import CryptoTestUtil
from unittest.case import TestCase

class HashTest(TestCase,BrowsingUtil, UserUtil, CryptoTestUtil):

    def giveHash(self):
        self.goToLoginPage()
        self.switchToTab('register')
        self.click("create_here")
        self.obtainHash("11111111110", "Mother Test", "registration-form")
        self.assertHashFromFormEquals("registration-form", config.testSignatureAllOne)

    
    def test_you_can_obtain_the_hash_by_filling_in_your_personal_id_and_pushing_the_button_near_it(self):
        """
        In this case your web browser goes directly to anchor.edemokraciagep.org, and gets the hash for you.
        The SSO server never sees your personal id.
        """
        self.giveHash()

    
    def test_if_you_give_hash_in_registration_you_will_have_a_hashgiven_assurance(self):
        self.goToLoginPage()
        self.switchToTab('register')
        mothername=self.createRandomUserId()
        self.registerUser(personalId="11111111110", motherName=mothername)
        self.assertPopupErrorMatchesRe("emailben megadott")
        self.closeMessage()
        self.assertElementMatchesRe("me_Data", "van Titkos K\xf3d")

    
    def test_if_you_give_hash_after_registration_you_will_have_a_hashgiven_assurance(self):
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
        time.sleep(4)
        self.click("changeHash")
        time.sleep(4)
        self.assertElementMatchesRe("change-hash-form_digest-pre", "[0-9a-f]{10}")
        self.switchToSection("account")
        time.sleep(2)
        self.assertElementMatchesRe("me_Data", "van Titkos K\xf3d")

    
    def test_assurer_can_obtain_the_hash_by_filling_in_your_personal_id__mother_name_and_pushing_the_button_near_it(self):
        self.loginWithPasswordAs(TE.assurerUser)
        self.switchToSection("assurer")
        self.obtainHash("22222222220", "Test Mother", "assurancing")
        self.wait_on_element_class(By.ID, 'assurance-giving_message', "given")

    
    def test_in_hash_collision_if_the_other_user_is_hand_assured_the_offender_receives_a_message(self):
        anotheruser = self.createUserWithCredentials().user
        digest = self.createHash()
        anotheruser.hash = digest
        Assurance.new(anotheruser, "test", anotheruser)
        anotheruser.save()
        self.goToLoginPage()
        self.switchToTab('register')
        self.registerUser()
        self.assertPopupErrorMatchesRe("emailben megadott")
        self.closeMessage()
        time.sleep(1)
        self.switchToSection("settings")
        self.click("viewChangeHashForm")
        self.fillInField("change-hash-form_digest_input",digest)
        self.click("changeHash")
        self.assertPopupErrorMatchesRe("megadta ezt a Titkos")

    def tearDown(self):
        BrowsingUtil.tearDown(self)
