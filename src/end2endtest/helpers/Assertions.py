import end2endtest.helpers.TestEnvironment as TE
import re
from selenium.webdriver.common.by import By

class Assertions(object):

    def assertEnoughTestRanAndNoneFailed(self, minOkay):
        body = self.observeField("qunit-testresult")
        numtests = int(re.search("(\d+) assertions", body).groups()[0])
        failed = int(re.search("(\d+) failed", body).groups()[0])
        self.assertTrue(numtests >= minOkay)
        self.assertTrue(failed == 0)

    def assertReachedRedirectUri(self):
        self.waitFortestAppRedirectUri()
        currentUri = TE.driver.current_url
        expectedUri = TE.app.redirect_uri.lower()
        self.assertTrue(currentUri.startswith(expectedUri))

    def assertHashFromFormEquals(self, formName, expectedSignature):
        elementId = formName + "_digest_input"
        self.waitUntilElementHasText(elementId)
        digest = self.observeFieldValue(elementId)
        self.assertEqual(digest, expectedSignature)

    def assertPopupTextIs(self, expectedText):
        body = self.observeField("PopupWindow_MessageDiv").strip()
        self.assertEqual(expectedText, body)

    def assertPopupMatchesRe(self, expectedRegEx):
        body = self.observeField("PopupWindow_SuccessDiv")
        self.assertRegexpMatches(body, expectedRegEx)

    def assertPopupErrorMatchesRe(self, expectedRegEx):
        self.assertElementMatchesRe("PopupWindow_ErrorDiv", expectedRegEx)

    def assertTextInPopupTitle(self, textToPresent):
        self.wait_on_element_text(By.ID, "PopupWindow_TitleDiv", textToPresent)
        body = self.observeField("PopupWindow_TitleDiv")
        self.assertEqual(textToPresent,body)
        
    def assertTextPresentInSuccessDiv(self, textToPresent):
        body = self.observeField("PopupWindow_SuccessDiv")
        self.assertTrue(textToPresent in body)

    def assertTextInMeMsg(self, textToFind):
        userdata = self.observeField("me_Msg")
        self.assertTrue(textToFind in userdata)

    def assertElementMatchesRe(self, fieldId, expectedRegEx):
        self.waitUntilElementEnabled(fieldId)
        body = self.observeField(fieldId)
        self.assertRegexpMatches(body, expectedRegEx)

    def assertElementMatches(self, fieldId, expectedRegEx):
        self.waitUntilElementEnabled(fieldId)
        body = self.observeField(fieldId)
        self.assertEqual(body, expectedRegEx)
