# pylint: disable=no-member
import os
from OpenSSL import crypto
from Crypto.Hash.SHA512 import SHA512Hash
from pdoauth.models.Credential import Credential
from test.helpers.FakeInterFace import FakeForm

TEST_USER_IDENTIFIER = \
    "06:11:50:AC:71:A4:CE:43:0F:62:DC:D2:B4:F0:2A:1C:31:4B:AB:E2/CI Test User"

SPKAC = """MIICSTCCATEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDt66ujL7Qi
gKPRoJzI7cdMFgxoNE7u5aKhAMLC7EE9Npn7Ig1Y6G5NIfjdWZy+Ryrw3/HdYRsS
9bL2LZb+w17lnrR8jv6kMRPuqw+tPGZMdri/QF6IZnbSa77zTLHB/z0Ffx/wgicX
Yp/XPJLwM0iNzanjnFoG1dlaQ8PL5lHbuHnorCpV9TbAzGkzofm059RxoHT8bes0
D4t4JzQaSKhpGf+w2SD2TlnxE9My1IK/q3UrgreBJ4Wn6CG0G6sTL2gw60oFr0Go
1n8ESRgXkt4DyiW5rjcj087WdxYYHYtJLv3czwSytvUeFfWl2EAtXJnH4AWuDS7S
iyT38IPwk8tZAgMBAAEWCTEyMzQ1Njc4OTANBgkqhkiG9w0BAQQFAAOCAQEA0kt4
sDLvT3ho/pxXIT14OcCtMxRvTq5CuEKrMICjnrOIwWcWLtjNBOTRW0cobEsn970k
vNjkzH/BnEzXwCqLPN0s6ctXHyTC8Y+528iFCw7R4nvMgAevqI4x1CNWB+/l0Hl5
0507mHjMJWSjqsW2RlQb/mp4S1rN8+VDja5hUCxRKc1/9omUht5EcygciMsKC79k
N8v6i3mEYWeRnsIXDfWpWZoejEm3cdlCr2sstFQ4GIzTw/KIHnEnkCOZWz8uQVIE
FiFJjirn+7QTlDjctU89Y4OqX2pufBxULSLMVnc8aM1/vXUDwtQKFuS1hr2DrUbb
JA3SM6HtjlWWGuocNw=="""

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
        return SHA512Hash(self.randString).hexdigest()

    def sslLoginWithCert(self, cert):
        environ = dict(SSL_CLIENT_CERT=cert)
        self.controller.interface.set_request_context(environ = environ)
        resp = self.controller.doSslLogin()
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

    def addCertCredential(self, email, user):
        data = dict(email=email, pubkey=SPKAC)
        self.controller.doKeygen(FakeForm(data))
        cred = Credential.getByUser(user, 'certificate')
        return cred
