from OpenSSL import crypto
class CertificateAuthority(object):
    INSTANCE = None
    def __init__(self, configOwner):
        pkeystring = configOwner.contentsOfFileNamedInConfig("CA_KEY_FILE")
        self.pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, pkeystring)
        cacertstring = configOwner.contentsOfFileNamedInConfig("CA_CERTIFICATE_FILE")
        self.cacert = crypto.load_certificate(crypto.FILETYPE_PEM, cacertstring)
        self.subject = self.cacert.get_subject()

    def signRequest(self, req, emailAddress):
        cert = crypto.X509()
        cert.set_serial_number(1)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(60)
        cert.set_issuer(self.subject)
        cert.get_subject().commonName = emailAddress
        cert.set_pubkey(req.get_pubkey())
        cert.sign(self.pkey, "sha512")
        return cert

    @classmethod
    def getInstance(cls, configOwner):
        if cls.INSTANCE is None:
            cls.INSTANCE = CertificateAuthority(configOwner)
        return cls.INSTANCE
