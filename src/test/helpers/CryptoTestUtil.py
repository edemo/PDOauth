# pylint: disable=no-member
import os
from OpenSSL import crypto
from Crypto.Hash.SHA512 import SHA512Hash
from pdoauth.models.Credential import Credential

TEST_USER_IDENTIFIER = \
    "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"

class CertAttributes(object):
    pass

class CryptoTestUtil(object):
    def getCertAttributes(self):
        ret = CertAttributes()
        dirName = os.path.dirname(__file__)
        certFileName = os.path.join(
            dirName, "..","..",
            "end2endtest", "client.crt")
        certFile = open(certFileName)
        ret.cert = certFile.read()
        certFile.close()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, ret.cert)
        ret.digest = x509.digest('sha1')
        commonName = x509.get_subject().commonName
        ret.identifier = "{0}/{1}".format(ret.digest,
            commonName)
        return ret

    def createHash(self):
        self.setupRandom()
        return SHA512Hash(self.randString).hexdigest() * 4

    def sslLoginWithCert(self, cert):
        environ = dict(SSL_CLIENT_CERT=cert)
        self.controller.interface.set_request_context(environ = environ)
        resp = self.controller.do_ssl_login()
        return resp

    def createUserAndLoginWithCert(self):
        certAttrs = self.getCertAttributes()
        self.identifier = certAttrs.identifier
        cred = self.createUserWithCredentials()
        secret = certAttrs.digest
        Credential.new(cred.user, "certificate", self.identifier, secret)
        resp = self.sslLoginWithCert(certAttrs.cert)
        return resp

    def removeCertUser(self):
        cred = Credential.get('certificate', TEST_USER_IDENTIFIER)
        if cred:
            cred.rm()
            cred.user.rm()


