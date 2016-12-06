from test.helpers.PDUnitTest import PDUnitTest
from pdoauth.ReportedError import ReportedError
from pdoauth.Decorators import Decorators
import logging
from pdoauth.app import app

class LoggerTest(PDUnitTest):

    def test_reportedError_logs(self):
        try:
            raise ReportedError("test")
        except ReportedError:
            raisePoint = Decorators.getRaisePoint()
        self.assertTrue('in test_reportedError_logs' in raisePoint, "raisePoint problem {0}".format(raisePoint))
        self.assertTrue('raise ReportedError("test")' in raisePoint, "raisePoint problem2 {0}".format(raisePoint))

    def test_log2(self):
        app.logger.info("hello")
        self.assertEqual(logging.DEBUG, app.logger.getEffectiveLevel())
