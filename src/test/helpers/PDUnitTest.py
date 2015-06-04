from twatson.unittest_annotations import Fixture, test  # @UnusedImport
from pdoauth.Controller import Controller
from pdoauth.FlaskInterface import FlaskInterface
from test.helpers.FakeInterFace import FakeInterface

class PDUnitTest(Fixture):
    def setUpController(self):
        Controller.unsetInterface(FlaskInterface)
        Controller.setInterface(FakeInterface)
        self.controller = Controller.getInstance()
    def tearDownController(self):
        Controller.unsetInterface(FakeInterface)
        Controller.setInterface(FlaskInterface)

