#pylint: disable=invalid-name, too-many-arguments
from pdoauth.models.Application import Application
from pdoauth.models.KeyData import KeyData
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.WebInterface import WebInterface
from pdoauth.Responses import Responses
from pdoauth.ReportedError import ReportedError
from pdoauth.CryptoUtils import CryptoUtils
from collections import namedtuple
from pdoauth.Messages import invalidGrant, invalidClient,\
    missingParameterUrlQuery, missingParameterResponse, missingParameterClientId,\
    missingRequiredParam, unsupportedGrantType, unsupportedResponseType,\
    unauthorizedClient, invalidRequest, invalidScope, accessDenied

TokenInfo = namedtuple('TokenInfo','access_token, token_type, expires_in, refresh_token')
class AuthProvider(WebInterface, Responses, CryptoUtils):

    @property
    def token_length(self):
        return 40

    @property
    def token_type(self):
        return 'Bearer'

    @property
    def token_expires_in(self):
        return 3600

    def auth_interface(self):
        uri = self.getRequestUrl()
        return self.get_authorization_code_from_uri(uri)

    def token_interface(self, requestForm):
        return self.get_token_from_post_data(requestForm)

    def get_authorization_code_from_uri(self, uri):
        params = self.getParamsOfUri(uri)
        self.validateUrlQueryParams(params)
        return self.get_authorization_code(**params)

    def get_authorization_code(self, response_type, client_id, redirect_uri, **params):
        client_id=client_id[0]
        response_type=response_type[0]
        redirect_uri=redirect_uri[0]
        scope = params.get('scope', [''])[0]
        self.validateGetAuthorizationCodeParameters(response_type, client_id, redirect_uri, params, scope)

        code = self.generateToken()
        self.persist_authorization_code(client_id=client_id, code=code, scope=scope)

        redirect = self.buildAuthorizationCodeRedirectUri(redirect_uri, params, code)
        return self.makeRedirectResponse(redirect)

    def isEmpty(self, value):
        return value is None or value == ''

    def get_token_from_post_data(self, form):
        self.ensureClientAuthParams(form)
        if form.scope.data is None:
            form.scope.data = ''
        if form.grant_type.data == "refresh_token":
            return self.refresh_token(form)

        self.ensureCustomerAuthParams(form)
        return self.get_token(form)

    def get_token(self, form):
        self.validateGetTokenParameters(form)
        if not form.code.data:
            raise ReportedError(invalidGrant, 400)
        data = self.from_authorization_code(form.client_id.data, form.code.data, form.scope.data)
        if self.isEmpty(data):
            raise ReportedError(invalidGrant, 400)
        self.discard_authorization_code(form.client_id.data, form.code.data)
        return self.persistAndRespond(form.client_id.data, data.user_id)

    def refresh_token(self, form):

        self.validateRefreshTokenParameters(form)
        keyData = self.from_refresh_token(form)

        if self.isEmpty(keyData):
            raise ReportedError(invalidGrant, 400)

        keyData.rm()

        return self.persistAndRespond(form.client_id.data, keyData.user_id)

    def persistAndRespond(self, clientId, userId):
        tokenInfo = TokenInfo(
            access_token = self.generateToken(),
            token_type = self.token_type,
            expires_in = self.token_expires_in,
            refresh_token = self.generateToken(),
        )
        self.persist_token_information(tokenInfo, clientId, userId)
        response = self.makeJsonResponse(tokenInfo._asdict())
        return response

    def persist_token_information(self, tokenInfo, clientId, userId):
        keydata = KeyData.new(clientId, userId, tokenInfo.access_token, tokenInfo.refresh_token)
        TokenInfoByAccessKey.new(tokenInfo.access_token, keydata, tokenInfo.expires_in)

    def from_refresh_token(self,form):
        return KeyData.find_by_refresh_token(form.client_id.data, form.refresh_token.data)

    def persist_authorization_code(self, client_id, code, scope):
        keyData = KeyData(client_id=client_id, authorization_code = code, user_id=self.getCurrentUser().userid)
        keyData.save()

    def from_authorization_code(self, client_id, code, scope):
        return KeyData.find_by_code(client_id=client_id,authorization_code = code)

    def discard_authorization_code(self, client_id, code):
        keydata = self.from_authorization_code(client_id, code, '')
        keydata.rm()

    def generateToken(self):
        return self.randomAsciiString(self.token_length)

    def buildAuthorizationCodeRedirectUri(self, redirect_uri, params, code):
        params.update({'code':code, 'response_type':None, 'client_id':None, 'redirect_uri':None})
        redirect = self.build_url(redirect_uri, params)
        return redirect

    def validateRefreshTokenParameters(self, form):
        self.validate_client_id(form.client_id.data, message=invalidClient, errorCode=400)
        self.validate_client_secret(form.client_id.data, form.client_secret.data)
        self.validate_scope(form.client_id.data, form.scope.data, errorCode=400)

    def validateGetTokenParameters(self, form):
        self.validate_redirect_uri(form.client_id.data, form.redirect_uri.data, message=invalidGrant, errorCode=400)
        self.ensureAuthorizationCodeGrantType(form.grant_type.data)
        self.validate_client_id(form.client_id.data, errorCode=400)
        self.validate_client_secret(form.client_id.data, form.client_secret.data)
        self.validate_scope(form.client_id.data, form.scope.data, errorCode=400)

    def validateGetAuthorizationCodeParameters(self, response_type, client_id, redirect_uri, params, scope):
        self.validate_redirect_uri(client_id, redirect_uri)
        self.validate_response_type(response_type, redirect_uri)
        self.validate_client_id(client_id)
        self.validate_access(redirect_uri)
        self.validate_scope(client_id, scope, uri=redirect_uri)

    def validateUrlQueryParams(self, params):
        if 'redirect_uri' not in params:
            raise ReportedError(missingParameterUrlQuery, 400)
        if 'response_type' not in params:
            raise ReportedError(missingParameterResponse, 302, params['redirect_uri'])
        if 'client_id' not in params:
            raise ReportedError(missingParameterClientId, 302, params['redirect_uri'])

    def ensureRequiredParam(self, form, name):
        if self.isEmpty(getattr(form,name).data):
            raise ReportedError("{0}: {1}".format(missingRequiredParam, name))

    def ensureClientAuthParams(self, form):
        for name in ['grant_type', 'client_id', 'client_secret']:
            self.ensureRequiredParam(form, name)

    def ensureCustomerAuthParams(self, data):
        for x in ['redirect_uri', 'code']:
            self.ensureRequiredParam(data, x)

    def ensureAuthorizationCodeGrantType(self, grant_type):
        if grant_type != 'authorization_code':
            raise ReportedError(unsupportedGrantType)

    def validate_response_type(self, response_type, url):
        if response_type != 'code':
            raise ReportedError(unsupportedResponseType, 302, uri=url)

    def validate_client_id(self, client_id, message=unauthorizedClient, errorCode=302, uri=None):
        app = Application.get(client_id)
        if self.isEmpty(app):
            raise ReportedError(unauthorizedClient, errorCode, uri=uri)

    def validate_client_secret(self,client_id, client_secret):
        app = Application.get(client_id)
        if app.secret != client_secret:
            raise ReportedError(invalidClient, 400)

    def validate_redirect_uri(self, client_id, redirect_uri, message=invalidRequest, errorCode=302):
        app = Application.get(client_id)
        if self.isEmpty(app):
            raise ReportedError(message, errorCode, uri=redirect_uri)
        if not app.redirect_uri == redirect_uri.split("?")[0]:
            raise ReportedError(message, errorCode, uri=redirect_uri)

    def validate_scope(self,client_id, scope, errorCode=302, uri=None):
        if not scope == "":
            raise ReportedError(invalidScope, errorCode, uri=uri)

    def validate_access(self, uri):
        if not self.getCurrentUser().is_authenticated:
            raise ReportedError(accessDenied, 302, uri=self.app.config.get('LOGIN_URL'))
