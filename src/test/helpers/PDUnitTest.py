from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from pdoauth.Controller import Controller, Interfaced
from pdoauth.FlaskInterface import FlaskInterface
from test.helpers.FakeInterFace import FakeInterface, FakeMailer, TestData
from pdoauth.ReportedError import ReportedError

class PDUnitTest(Fixture):
    def setUp(self):
        self.setUpController()
    def tearDown(self):
        self.tearDownController()

    def setUpController(self):
        Interfaced.unsetInterface(FlaskInterface)
        Interfaced.setInterface(FakeInterface)
        FakeInterface._testdata = TestData()
        self.controller = Controller.getInstance()
        self.oldmail = getattr(self.controller,"mail", None)
        self.controller.mail = FakeMailer()

    def tearDownController(self):
        Interfaced.unsetInterface(FakeInterface)
        Interfaced.setInterface(FlaskInterface)
        self.controller.mail = self.oldmail

    def assertReportedError(self, funct, args, status, descriptor):
        with self.assertRaises(ReportedError) as e:
            funct(*args)
        self.assertEquals(e.exception.status, status)
        self.assertEqual(descriptor, e.exception.descriptor)

