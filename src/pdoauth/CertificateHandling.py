from pdoauth.models.Credential import Credential
from pdoauth.forms.KeygenForm import KeygenForm
from pdoauth.Decorators import Decorators
import urlparse
from pdoauth.ReportedError import ReportedError
from pdoauth.CredentialManager import CredentialManager
from pdoauth.CryptoUtils import CryptoUtils

class CertificateHandling(CryptoUtils):
    def addCertCredentialToUser(self, cert, user):
        identifier, digest = self.parseCert(cert)
        Credential.new(user, "certificate", identifier, digest)

    def registerAndLoginCertUser(self, email, cert):
        cred = self.registerCertUser(cert, [email])
        self.loginUser(cred.user)

    def extractCertFromForm(self, form):
        email = form.email.data
        spkacInput = form.pubkey.data
        certObj = self.createCertFromSPKAC(spkacInput, email, email)
        certAsPem = certObj.as_pem()
        return certAsPem, certObj

    def createCertResponse(self, certObj):
        resp = self.make_response(certObj.as_der(), 200)
        resp.headers["Content-Type"] = "application/x-x509-user-cert"
        return resp

    @Decorators.formValidated(KeygenForm)
    @Decorators.exceptionChecked
    def do_keygen(self, form):
        email = form.email.data
        certAsPem, certObj = self.extractCertFromForm(form)
        user = self.getCurrentUser()
        if user.is_authenticated():
            self.addCertCredentialToUser(certAsPem, user)
        else:
            self.registerAndLoginCertUser(email, certAsPem)
        return self.createCertResponse(certObj)

    def getEmailFromQueryParameters(self):
        parsed = urlparse.urlparse(self.getRequestUrl())
        email = urlparse.parse_qs(parsed.query).get('email', None)
        return email

    def registerCertUser(self, cert, email):
        if cert is None or cert == '':
            raise ReportedError(["No certificate given"], 403)
        identifier, digest = self.parseCert(cert)
        cred = Credential.get("certificate", identifier)
        if cred is None:
            if email is None:
                raise ReportedError(["You have to register first"], 403)
            theEmail = email[0]
            CredentialManager.create_user_with_creds("certificate", identifier, digest, theEmail)
            cred = Credential.get("certificate", identifier)
            self.sendPasswordVerificationEmail(cred.user)
        cred.user.activate()
        return cred

    def do_ssl_login(self):
        cert = self.getEnvironmentVariable('SSL_CLIENT_CERT')
        email = self.getEmailFromQueryParameters()
        cred = self.registerCertUser(cert, email)
        resp = self.finishLogin(cred.user)
        resp.headers['Access-Control-Allow-Origin']="*"
        return resp
