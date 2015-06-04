from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from pdoauth.Controller import Controller
from pdoauth.FlaskInterface import FlaskInterface
from test.helpers.FakeInterFace import FakeInterface, FakeMailer, TestData

class PDUnitTest(Fixture):
    def setUp(self):
        self.setUpController()
    def tearDown(self):
        self.tearDownController()

    def setUpController(self):
        Controller.unsetInterface(FlaskInterface)
        Controller.setInterface(FakeInterface)
        FakeInterface._testdata = TestData()
        self.controller = Controller.getInstance()
        self.oldmail = self.controller.mail
        self.controller.mail = FakeMailer()

    def tearDownController(self):
        Controller.unsetInterface(FakeInterface)
        Controller.setInterface(FlaskInterface)
        self.controller.mail = self.oldmail

