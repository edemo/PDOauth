#pylint: disable=unused-import, star-args
from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from pdoauth.Controller import Controller
from pdoauth.ReportedError import ReportedError
from test.helpers.FakeInterFace import FakeInterface, FakeApp, FakeMail
from pdoauth import main  # @UnusedImport

class PDUnitTest(Fixture):
    def setUp(self):
        self.setUpController()

    def setUpController(self):
        self.controller = Controller(FakeInterface())
        self.controller.app = FakeApp()
        self.controller.app = FakeApp()
        self.controller.mail = FakeMail()

    def assertReportedError(self, funct, args, status, descriptor):
        with self.assertRaises(ReportedError) as context:
            funct(*args)
        self.assertEqual(descriptor, context.exception.descriptor)
        self.assertEqual(context.exception.status, status)

