from pyspkac.spkac import SPKAC
#pylint: disable=no-member
from M2Crypto import EVP, X509
from OpenSSL import crypto
import time
from pdoauth.ReportedError import ReportedError
from string import ascii_letters, digits
import random
from pdoauth.Messages import errorInCert

UNICODE_ASCII_CHARACTERS = (ascii_letters.decode('ascii') +  # @UndefinedVariable
    digits.decode('ascii'))


class CryptoUtils(object):

    def randomAsciiString(self, length):
        return ''.join([random.choice(UNICODE_ASCII_CHARACTERS) for x in xrange(length)])  # @UnusedVariable

    def contentsOfFileNamedInConfig(self, confkey):
        decorated = open(self.getConfig(confkey))
        ret = decorated.read()
        decorated.close()
        return ret

    def createCertFromSPKAC(self, spkacInput, commonName, email):
        if email is None:
            theSPKAC = SPKAC(spkacInput, CN=commonName)
        else:
            theSPKAC = SPKAC(spkacInput, CN=commonName, Email=email)
        ca_crt = X509.load_cert_string(self.contentsOfFileNamedInConfig("CA_CERTIFICATE_FILE"))
        ca_pkey = EVP.load_key_string(self.contentsOfFileNamedInConfig("CA_KEY_FILE"))
        now = int(time.time())
        serial = now
        notAfter = now + 60 * 60 * 24 * 365 * 2
        certObj = theSPKAC.gen_crt(ca_pkey, ca_crt, serial, now, notAfter, 'sha1')
        return certObj

    def parseCert(self, cert):
        try:
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        except Exception:
            raise ReportedError([errorInCert, cert],400)
        digest = x509.digest('sha1')
        commonName = x509.get_subject().commonName.encode('raw_unicode_escape').decode('utf-8')
        identifier = u"{0}/{1}".format(digest, commonName)
        return identifier, digest
