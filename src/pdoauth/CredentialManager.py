from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential

class CredentialManager(object):
    @classmethod
    def protect_secret(cls, secret):
        protected = SHA256Hash(secret).hexdigest()
        return protected

    @classmethod
    def create_user_with_creds(cls, credtype, identifier, secret, email, digest=None):
        user = User.new(email, digest)
        protected = cls.protect_secret(secret)
        Credential.new(user, credtype, identifier, protected)
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
