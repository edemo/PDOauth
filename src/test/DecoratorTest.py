from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.Decorators import Decorators
from test.helpers.FakeInterFace import FakeApp, FakeInterface
from pdoauth.ReportedError import ReportedError

class CredentialTest(PDUnitTest):
    def assertNoCacheHeaders(self, resp):
        self.assertEqual("no-cache, no-store, must-revalidate", resp.headers['Cache-Control'])
        self.assertEqual("no-cache", resp.headers['Pragma'])
        self.assertEqual("0", resp.headers['Expires'])

    def setUp(self):
        self.decorator = Decorators(FakeApp(), FakeInterface())
        PDUnitTest.setUp(self)

    @test
    def decorator_returns_cache_control_headers(self):
        resp = self.decorator.runInterfaceFunc(self.aFunc, list(), dict(), None, 200, None)
        self.assertNoCacheHeaders(resp)

    @test
    def decorator_returns_cache_control_header_in_error(self):
        resp = self.decorator.runInterfaceFunc(self.anErringFunc, list(), dict(), None, 200, None)
        self.assertNoCacheHeaders(resp)
                  
    def aFunc(self,*args,**kwargs):
        return self.controller.make_response("hello world", 200)

    def anErringFunc(self,*args,**kwargs):
        raise ReportedError("example error")
