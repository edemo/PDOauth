from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential
from uuid import uuid4
import time


class CredentialManager(object):
    fourDaysInSeconds = 60 * 60 * 24 * 4
    fourHoursInSeconds = 14400

    @classmethod
    def protect_secret(cls, secret):
        protected = SHA256Hash(bytes(secret,'UTF-8')).hexdigest()
        return protected

    @classmethod
    def addCredToUser(cls, user, credtype, identifier, secret):
        protected = cls.protect_secret(secret)
        cred = Credential.new(user, credtype, identifier, protected)
        cred.save()
        return cred

    @classmethod
    def create_user_with_creds(cls, credtype, identifier, secret, email, digest=None):
        user = User.new(email, digest)
        cred = cls.addCredToUser(user, credtype, identifier, secret)
        return cred

    @staticmethod
    def createTemporaryCredential(user, credentialType, expiry=fourDaysInSeconds, additionalInfo=None):
        secret = uuid4().hex
        expiry = time.time() + expiry
        Credential.new(user, credentialType, str(expiry)+":"+str(additionalInfo), secret)
        return secret, expiry


    
    @classmethod
    def getCredentialFromForm(cls, form):
        cred = Credential.get('password', form.identifier.data)
        if cred is None:
            user = User.getByEmail(form.identifier.data)
            if user is None:
                return None
            cred = Credential.getByUser(user, "password")
            if cred is None:
                return None
        hashed = cls.protect_secret(form.password.data)
        if cred.secret == hashed:
            return cred
        return None
