import os
from OpenSSL import crypto
from Crypto.Hash.SHA512 import SHA512Hash
from pdoauth.models.Credential import Credential

class CryptoTestUtil(object):
    def getCertAttributes(self):
        certFileName = os.path.join(os.path.dirname(__file__), "..","..", "end2endtest", "client.crt")
        certFile = open(certFileName)
        cert = certFile.read()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        digest = x509.digest('sha1')
        cn = x509.get_subject().commonName
        identifier = "{0}/{1}".format(digest, 
            cn)
        certFile.close()
        return identifier, digest, cert

    def createHash(self):
        return SHA512Hash(self.randString).hexdigest() * 4

    def sslLoginWithCert(self, cert):
        self.controller.interface.set_request_context(environ = dict(SSL_CLIENT_CERT=cert))
        resp = self.controller.do_ssl_login()
        return resp

    def createUserAndLoginWithCert(self):
        identifier, digest, cert = self.getCertAttributes()
        user = self.createUserWithCredentials()
        secret = digest
        Credential.new(user, "certificate", identifier, secret)
        resp = self.sslLoginWithCert(cert)
        return resp

