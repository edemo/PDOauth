
from pyoauth2_shift.provider import AuthorizationProvider
from pdoauth.models.Application import Application

class AuthProvider(AuthorizationProvider):

    def validate_client_id(self,client_id):
        if client_id is None:
            return False
        app = Application.find(client_id)
        return app
    def validate_client_secret(self,client_id,client_secret):
        if client_id is None:
            return False
        app = Application.find(client_id)
        return app.secret == client_secret
