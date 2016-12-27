#pylint: disable=no-member
from pdoauth.models.Credential import Credential
from pdoauth.ReportedError import ReportedError
from pdoauth.CredentialManager import CredentialManager
from pdoauth.CryptoUtils import CryptoUtils
from pdoauth.Messages import noCertificateGiven, errorInCert
from pdoauth.LoginHandling import youHaveToRegisterFirst
from OpenSSL import crypto
from pdoauth.CertificateAuthority import CertificateAuthority
import uritools

class CertificateHandling(CryptoUtils):

    def getDigest(self, cert):
        try:
            digest = cert.digest("sha512").decode('utf-8')
            return digest
        except:
            raise ReportedError(errorInCert)

    def getIdentifier(self, cert):
        try:
            cn = cert.get_subject().commonName
            digest = self.getDigest(cert)
            identifier = "{0}/{1}".format(cn, digest)
            return identifier
        except:
            raise ReportedError(errorInCert)

    def addCertCredentialToUser(self, cert, user):
        identifier = self.getIdentifier(cert)
        digest = self.getDigest(cert)
        Credential.new(user, "certificate", identifier, digest)

    def registerAndLoginCertUser(self, form, cert):
        cred = self.loginOrRegisterCertUser(cert, [form.email.data])
        digestField = getattr(form, "digest", False)
        if cred and digestField and digestField.data:
            self.checkAndUpdateHash(form,cred.user)
        self.loginUser(cred)

    def addHeadersToCertResponse(self, resp):
        resp.headers["Content-Type"] = "application/x-x509-user-cert"
        self.setCSRFCookie(resp)

    def getEmailFromQueryParameters(self):
        requestUrl = self.getRequestUrl()
        parsed = uritools.urisplit(requestUrl)
        email = parsed.getquerydict().get('email')
        return email


    def registerCertUser(self, email, identifier, digest, cred):
        if email is None:
            raise ReportedError([youHaveToRegisterFirst], 403)
        theEmail = email[0]
        CredentialManager.create_user_with_creds("certificate", identifier, digest, theEmail)
        cred = Credential.get("certificate", identifier)
        self.sendPasswordVerificationEmail(cred.user)
        return cred

    def loginOrRegisterCertUser(self, cert, email):
        if cert is None or cert == '':
            raise ReportedError([noCertificateGiven], 403)
        identifier = self.getIdentifier(cert)
        cred = Credential.get("certificate", identifier)
        if cred is None:
            digest = self.getDigest(cert)
            cred = self.registerCertUser(email, identifier, digest, cred)
        cred.user.activate()
        return cred

    def doSslLogin(self):
        certtext = self.getEnvironmentVariable('SSL_CLIENT_CERT')
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM,certtext)
        except:
            raise ReportedError(errorInCert)
        email = self.getEmailFromQueryParameters()
        cred = self.loginOrRegisterCertUser(cert, email)
        resp = self.finishLogin(cred)
        resp.headers['Access-Control-Allow-Origin']="*"
        return resp

    def createCertFromReq(self, reqstring, email):
        req = crypto.load_certificate_request(crypto.FILETYPE_PEM, reqstring)
        cacert = CertificateAuthority.getInstance(self)
        cert = cacert.signRequest(req, email)
        return cert

    def createCertResponse(self, cert):
        resp = self.make_response(crypto.dump_certificate(crypto.FILETYPE_ASN1,cert), 200)
        self.addHeadersToCertResponse(resp)
        return resp

    def signRequest(self,form):
        try:
            cert = self.createCertFromReq(form.pubkey.data, form.email.data)
        except Exception:
            raise ReportedError(errorInCert)
        user = self.getCurrentUser()
        if user.is_authenticated:
            self.addCertCredentialToUser(cert, user)
        else:
            self.registerAndLoginCertUser(form, cert)
        return self.createCertResponse(cert)
