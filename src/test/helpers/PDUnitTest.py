from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from pdoauth.Controller import Controller
from test.helpers.FakeInterFace import FakeInterface, FakeApp
from pdoauth.ReportedError import ReportedError

class PDUnitTest(Fixture):
    def setUp(self):
        self.setUpController()

    def setUpController(self):
        self.controller = Controller(FakeInterface)
        self.controller.app = FakeApp()


    def assertReportedError(self, funct, args, status, descriptor):
        with self.assertRaises(ReportedError) as e:
            funct(*args)
        self.assertEquals(e.exception.status, status)
        self.assertEqual(descriptor, e.exception.descriptor)

