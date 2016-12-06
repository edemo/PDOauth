from OpenSSL import crypto
import time
from pdoauth.ReportedError import ReportedError
from string import ascii_letters, digits
import random
from pdoauth.Messages import errorInCert

UNICODE_ASCII_CHARACTERS = ascii_letters + digits


class CryptoUtils(object):

    @staticmethod
    def randomAsciiString(length):
        return ''.join([random.choice(UNICODE_ASCII_CHARACTERS) for x in range(length)])  # @UnusedVariable

    def contentsOfFileNamedInConfig(self, confkey):
        theFile = open(self.getConfig(confkey))
        ret = theFile.read()
        theFile.close()
        return ret
