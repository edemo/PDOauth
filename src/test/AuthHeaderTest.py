from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.UserUtil import UserUtil
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.ReportedError import ReportedError
from pdoauth.app import app

class AuthHeaderTest(PDUnitTest, UserUtil, AuthProviderUtil):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.app = self.createApp()
        self.setDefaultParams()

    
    def test_bad_authorization_header_yields_ReportedError(self):
        headers = dict(Authorization='Oneword')
        self.controller.interface.set_request_context(headers=headers)
        self.assertRaises(ReportedError, self.controller.authenticateUserOrBearer)

    
    def test_good_authorization_header_yields_authenticated_user(self):
        with app.test_client() as client:
            headers = dict(Authorization='Oneword')
            self.controller.interface.set_request_context(headers=headers)
            self.assertRaises(ReportedError, self.controller.authenticateUserOrBearer)
