#pylint: disable=unused-import, star-args
from pdoauth.Controller import Controller
from pdoauth.ReportedError import ReportedError
from test.helpers.FakeInterFace import FakeInterface, FakeApp, FakeMail
from pdoauth import main  # @UnusedImport
from unittest.case import TestCase

class PDUnitTest(TestCase):
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

