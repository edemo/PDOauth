from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential

class CredentialManager(object):
    @classmethod
    def protect_secret(cls, secret):
        protected = SHA256Hash(secret).hexdigest()
        return protected

    @classmethod
    def addCredToUser(cls, user, credtype, identifier, secret):
        protected = cls.protect_secret(secret)
        cred = Credential.new(user, credtype, identifier, protected)
        cred.save()
        return user

    @classmethod
    def create_user_with_creds(cls, credtype, identifier, secret, email, digest=None):
        user = User.new(email, digest)
        user = cls.addCredToUser(user, credtype, identifier, secret)
        return user

    
    @classmethod
    def validate_from_form(cls, form):
        cred = Credential.get('password', form.identifier.data)
        if cred is None:
            return None
        hashed = cls.protect_secret(form.secret.data)
        if cred.secret == hashed:
            return cred.user
        return None
