import end2endtest.helpers.TestEnvironment as TE
import re

class Assertions(object):

    def assertEnoughTestRanAndNoneFailed(self):
        body = self.observeField("qunit-testresult")
        numtests = int(re.search("(\d+) assertions", body).groups()[0])
        failed = int(re.search("(\d+) failed", body).groups()[0])
        self.assertTrue(numtests > 40)
        self.assertTrue(failed == 0)

    def assertReachedRedirectUri(self):
        self.waitFortestAppRedirectUri()
        currentUri = TE.driver.current_url
        expectedUri = TE.app.redirect_uri.lower()
        self.assertTrue(currentUri.startswith(expectedUri))

    def assertHashFromFormEquals(self, formName, expectedSignature):
        digest = self.observeFieldValue(formName + "_digest_input")
        self.assertEqual(digest, expectedSignature)

    def assertPopupTextIs(self, expectedText):
        body = self.observeField("PopupWindow_MessageDiv")
        self.assertEqual(expectedText, body)

    def assertPopupMatchesRe(self, expectedRegEx):
        body = self.observeField("PopupWindow_SuccessDiv")
        self.assertRegexpMatches(body, expectedRegEx)

    def assertTextPresentInSuccessDiv(self, textToPresent):
        body = self.observeField("PopupWindow_SuccessDiv")
        self.assertTrue(textToPresent in body)

    def assertTextInMeMsg(self, textToFind):
        userdata = self.observeField("me_Msg")
        self.assertTrue(textToFind in userdata)
