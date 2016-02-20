from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.ReportedError import ReportedError

class AuthHeaderTest(PDUnitTest, UserUtil, AuthProviderUtil):

    def setUp(self):
        PDUnitTest.setUp(self)
        self.app = self.createApp()
        self.setDefaultParams()

    @test
    def bad_authorization_header_yields_ReportedError(self):
        headers = dict(Authorization='Oneword')
        self.controller.interface.set_request_context(headers=headers)
        self.assertRaises(ReportedError, self.controller.authenticateUserOrBearer)
