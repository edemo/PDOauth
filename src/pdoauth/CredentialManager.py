from Crypto.Hash.SHA256 import SHA256Hash
from pdoauth.models.User import User
from pdoauth.models.Credential import Credential

class CredentialManager(object):
    @classmethod
    def protect_secret(cls, credtype, identifier, secret):
        return SHA256Hash(secret).hexdigest()

    @classmethod
    def create_user_with_creds(cls, credtype, identifier, secret, email, digest=None):
        user = User.new(email, digest)
        protected = cls.protect_secret(credtype, identifier, secret)
        cred = Credential.new(user, credtype, identifier, protected)
        if cred is None:
            user.rm()
            return None
        return user

    
    @classmethod
    def validate_from_form(cls, form):
        cred = Credential.get('password', form.username.data)
        if cred is None:
            return None
        hashed = cls.protect_secret('password', form.username.data, form.password.data)
        if cred.secret == hashed:
            return cred.user
        return None

    
    @classmethod
    def create_from_form(cls, form):
        existingUser = User.getByEmail(form.email.data)
        if existingUser:
            return None
        return cls.create_user_with_creds(
            form.credentialType.data,
            form.identifier.data,
            form.secret.data,
            form.email.data,
            form.digest.data)
    
    
    
    
    
    
    
    
