
from pyoauth2_shift.provider import AuthorizationProvider
from pdoauth.models.Application import Application
from flask.globals import session

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
        return app.redirect_uri == redirect_uri.split("?")[0]
    
    def validate_scope(self,client_id, scope):
        return scope == ""
    
    def validate_access(self):
        return getattr(session, 'user', None) is not None