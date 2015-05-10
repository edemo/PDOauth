
from pyoauth2_shift.provider import AuthorizationProvider
from pdoauth.models.Application import Application
from flask.globals import request
from pdoauth.models.KeyData import KeyData
from flask_login import current_user
import flask
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey

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
        return current_user.is_authenticated()

    def persist_token_information(self, client_id, scope, access_token, token_type, expires_in, refresh_token, data):
        keydata = KeyData.new(client_id, data.user_id, access_token, refresh_token)
        TokenInfoByAccessKey.new(access_token, keydata, expires_in)

    
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
        keyData = KeyData(client_id=client_id, authorization_code = code, user_id=current_user.userid)
        keyData.save()

    def from_authorization_code(self, client_id, code, scope):
        return KeyData.find_by_code(client_id=client_id,authorization_code = code)

    def discard_authorization_code(self, client_id, code):
        keydata = self.from_authorization_code(client_id, code, '')
        keydata.rm()
        
    @staticmethod
    def auth_interface():
        provider = AuthProvider()
        response = provider.get_authorization_code_from_uri(request.url)
        flask_res = flask.make_response(response.text, response.status_code)
        for k, v in response.headers.iteritems():
            flask_res.headers[k] = v
        
        return flask_res

    @staticmethod
    def token_interface():
        provider = AuthProvider()
        data = {k:request.form[k] for k in request.form.iterkeys()}
        response = provider.get_token_from_post_data(data)
        flask_res = flask.make_response(response.text, response.status_code)
        for k, v in response.headers.iteritems():
            flask_res.headers[k] = v
        
        return flask_res
