
from pyoauth2_shift.provider import AuthorizationProvider
from pdoauth.models.Application import Application
from flask.globals import session
from pdoauth.models.KeyData import KeyData

class ScopeMustBeEmpty(Exception):
    pass


class DiscardingNonexistingToken(Exception):
    pass


class AuthProvider(AuthorizationProvider):

    def validate_client_id(self,client_id):
        if client_id is None:
            return False
        app = Application.get(client_id)
        return app
    def validate_client_secret(self,client_id,client_secret):
        if client_id is None:
            return False
        app = Application.get(client_id)
        return app.secret == client_secret
    
    def validate_redirect_uri(self,client_id,redirect_uri):
        if client_id is None or\
           redirect_uri is None:
            return False
        app = Application.get(client_id)
        if app is None:
            return False
        return app.redirect_uri == redirect_uri.split("?")[0]
    
    def validate_scope(self,client_id, scope):
        return scope == ""
    
    def validate_access(self):
        return getattr(session, 'user', None) is not None

    def persist_token_information(self, client_id, scope, access_token, token_type, expires_in, refresh_token, data):
        KeyData.new(client_id, session.user.id, access_token, refresh_token)
    
    def from_refresh_token(self,client_id, refresh_token, scope):
        if scope != '':
            raise ScopeMustBeEmpty()
        return KeyData.find_by_refresh_token(client_id, refresh_token)
    
    def discard_refresh_token(self, client_id, refresh_token):
        keyData = self.from_refresh_token(client_id, refresh_token, '')
        if keyData is None:
            raise DiscardingNonexistingToken()
        keyData.rm()
        
    def persist_authorization_code(self, client_id, code, scope):
        keyData = KeyData(client_id=client_id, authorization_code = code, user_id=session.user.id)
        keyData.save()

    def from_authorization_code(self, client_id, code, scope):
        return KeyData.find_by_code(client_id=client_id,authorization_code = code)