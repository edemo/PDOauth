import urlparse
from pdoauth.WebInterface import WebInterface
import random
import string
from pdoauth.ReportedError import ReportedError
import urllib
from pdoauth.Responses import Responses

UNICODE_ASCII_CHARACTERS = (string.ascii_letters.decode('ascii') +
    string.digits.decode('ascii'))

class AuthorizationProvider(WebInterface, Responses):
    """OAuth 2.0 authorization provider. This class manages authorization
    codes and access tokens. Certain methods MUST be overridden in a
    subclass, thus this class cannot be directly used as a provider.

    These are the methods that must be implemented in a subclass:

        validate_client_id(self, client_id)
            # Return True or False

        validate_client_secret(self, client_id, client_secret)
            # Return True or False

        validate_scope(self, client_id, scope)
            # Return True or False

        validate_redirect_uri(self, client_id, redirect_uri)
            # Return True or False

        validate_access(self)  # Use this to validate your app session user
            # Return True or False

        from_authorization_code(self, client_id, code, scope)
            # Return mixed data or None on invalid

        from_refresh_token(self, client_id, refresh_token, scope)
            # Return mixed data or None on invalid

        persist_authorization_code(self, client_id, code, scope)
            # Return value ignored

        persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in, refresh_token,
                                  data)
            # Return value ignored

        discard_authorization_code(self, client_id, code)
            # Return value ignored

        discard_refresh_token(self, client_id, refresh_token)
            # Return value ignored

    Optionally, the following may be overridden to acheive desired behavior:

        @property
        token_length(self)

        @property
        token_type(self)

        @property
        token_expires_in(self)

        generate_authorization_code(self)

        generate_access_token(self)

        generate_refresh_token(self)

    """

    @property
    def token_length(self):
        """Property method to get the length used to generate tokens.

        :rtype: int
        """
        return 40

    @property
    def token_type(self):
        """Property method to get the access token type.

        :rtype: str
        """
        return 'Bearer'

    @property
    def token_expires_in(self):
        """Property method to get the token expiration time in seconds.

        :rtype: int
        """
        return 3600

    def random_ascii_string(self, length):
        return ''.join([random.choice(UNICODE_ASCII_CHARACTERS) for x in xrange(length)])

    def generate_authorization_code(self):
        """Generate a random authorization code.

        :rtype: str
        """
        return self.random_ascii_string(self.token_length)

    def generate_access_token(self):
        """Generate a random access token.

        :rtype: str
        """
        return self.random_ascii_string(self.token_length)

    def generate_refresh_token(self):
        """Generate a random refresh token.

        :rtype: str
        """
        return self.random_ascii_string(self.token_length)

    def get_authorization_code(self,
                               response_type,
                               client_id,
                               redirect_uri,
                               **params):
        """Generate authorization code HTTP response.

        :param response_type: Desired response type. Must be exactly "code".
        :type response_type: str
        :param client_id: Client ID.
        :type client_id: str
        :param redirect_uri: Client redirect URI.
        :type redirect_uri: str
        :rtype: requests.Response
        """

        # Ensure proper response_type
        if response_type != 'code':
            err = 'unsupported_response_type'
            return self._make_redirect_error_response(redirect_uri, err)

        # Check redirect URI
        is_valid_redirect_uri = self.validate_redirect_uri(client_id,
                                                           redirect_uri)
        if not is_valid_redirect_uri:
            return self._invalid_redirect_uri_response()

        # Check conditions
        is_valid_client_id = self.validate_client_id(client_id)
        is_valid_access = self.validate_access()
        scope = params.get('scope', '')
        is_valid_scope = self.validate_scope(client_id, scope)

        # Return proper error responses on invalid conditions
        if not is_valid_client_id:
            err = 'unauthorized_client'
            raise ReportedError('unauthorized_client', 302)

        if not is_valid_access:
            raise ReportedError('access_denied', 302)

        if not is_valid_scope:
            raise ReportedError('invalid_scope', 302)

        # Generate authorization code
        code = self.generate_authorization_code()

        # Save information to be used to validate later requests
        self.persist_authorization_code(client_id=client_id,
                                        code=code,
                                        scope=scope)

        # Return redirection response
        params.update({
            'code': code,
            'response_type': None,
            'client_id': None,
            'redirect_uri': None
        })
        redirect = self.build_url(redirect_uri, params)
        return self.makeRedirectResponse(redirect)

    def build_url(self, base, additional_params=None):
        """Construct a URL based off of base containing all parameters in
        the query portion of base plus any additional parameters.
    
        :param base: Base URL
        :type base: str
        ::param additional_params: Additional query parameters to include.
        :type additional_params: dict
        :rtype: str
        """
        url = urlparse.urlparse(base)
        query_params = {}
        query_params.update(urlparse.parse_qsl(url.query, True))
        if additional_params is not None:
            query_params.update(additional_params)
            for k, v in additional_params.iteritems():
                if v is None:
                    query_params.pop(k)
    
        return urlparse.urlunparse((url.scheme,
                                    url.netloc,
                                    url.path,
                                    url.params,
                                    urllib.urlencode(query_params),
                                    url.fragment))

    def refresh_token(self,
                      grant_type,
                      client_id,
                      client_secret,
                      refresh_token,
                      **params):
        """Generate access token HTTP response from a refresh token.

        :param grant_type: Desired grant type. Must be "refresh_token".
        :type grant_type: str
        :param client_id: Client ID.
        :type client_id: str
        :param client_secret: Client secret.
        :type client_secret: str
        :param refresh_token: Refresh token.
        :type refresh_token: str
        :rtype: requests.Response
        """

        # Ensure proper grant_type
        if grant_type != 'refresh_token':
            return self._make_json_error_response('unsupported_grant_type')

        # Check conditions
        is_valid_client_id = self.validate_client_id(client_id)
        is_valid_client_secret = self.validate_client_secret(client_id,
                                                             client_secret)
        scope = params.get('scope', '')
        is_valid_scope = self.validate_scope(client_id, scope)
        data = self.from_refresh_token(client_id, refresh_token, scope)
        is_valid_refresh_token = data is not None

        # Return proper error responses on invalid conditions
        if not (is_valid_client_id and is_valid_client_secret):
            return self._make_json_error_response('invalid_client')

        if not is_valid_scope:
            return self._make_json_error_response('invalid_scope')

        if not is_valid_refresh_token:
            return self._make_json_error_response('invalid_grant')

        # Discard original refresh token
        self.discard_refresh_token(client_id, refresh_token)

        # Generate access tokens once all conditions have been met
        access_token = self.generate_access_token()
        token_type = self.token_type
        expires_in = self.token_expires_in
        refresh_token = self.generate_refresh_token()

        # Save information to be used to validate later requests
        self.persist_token_information(client_id=client_id,
                                       scope=scope,
                                       access_token=access_token,
                                       token_type=token_type,
                                       expires_in=expires_in,
                                       refresh_token=refresh_token,
                                       data=data)

        # Return json response
        return self._make_json_response({
            'access_token': access_token,
            'token_type': token_type,
            'expires_in': expires_in,
            'refresh_token': refresh_token
        })

    def get_token(self,
                  grant_type,
                  client_id,
                  client_secret,
                  redirect_uri,
                  code,
                  **params):
        """Generate access token HTTP response.

        :param grant_type: Desired grant type. Must be "authorization_code".
        :type grant_type: str
        :param client_id: Client ID.
        :type client_id: str
        :param client_secret: Client secret.
        :type client_secret: str
        :param redirect_uri: Client redirect URI.
        :type redirect_uri: str
        :param code: Authorization code.
        :type code: str
        :rtype: requests.Response
        """

        # Ensure proper grant_type
        if grant_type != 'authorization_code':
            return self._make_json_error_response('unsupported_grant_type')

        # Check conditions
        is_valid_client_id = self.validate_client_id(client_id)
        is_valid_client_secret = self.validate_client_secret(client_id,
                                                             client_secret)
        is_valid_redirect_uri = self.validate_redirect_uri(client_id,
                                                           redirect_uri)

        scope = params.get('scope', '')
        is_valid_scope = self.validate_scope(client_id, scope)
        data = self.from_authorization_code(client_id, code, scope)
        is_valid_grant = data is not None

        # Return proper error responses on invalid conditions
        if not (is_valid_client_id and is_valid_client_secret):
            return self._make_json_error_response('invalid_client')

        if not is_valid_grant or not is_valid_redirect_uri:
            return self._make_json_error_response('invalid_grant')

        if not is_valid_scope:
            return self._make_json_error_response('invalid_scope')

        # Discard original authorization code
        self.discard_authorization_code(client_id, code)

        # Generate access tokens once all conditions have been met
        access_token = self.generate_access_token()
        token_type = self.token_type
        expires_in = self.token_expires_in
        refresh_token = self.generate_refresh_token()

        # Save information to be used to validate later requests
        self.persist_token_information(client_id=client_id,
                                       scope=scope,
                                       access_token=access_token,
                                       token_type=token_type,
                                       expires_in=expires_in,
                                       refresh_token=refresh_token,
                                       data=data)

        # Return json response
        return self.makeJsonResponse({
            'access_token': access_token,
            'token_type': token_type,
            'expires_in': expires_in,
            'refresh_token': refresh_token
        })

    def get_authorization_code_from_uri(self, uri):
        """Get authorization code response from a URI. This method will
        ignore the domain and path of the request, instead
        automatically parsing the query string parameters.

        :param uri: URI to parse for authorization information.
        :type uri: str
        :rtype: requests.Response
        """
        params = dict(urlparse.parse_qsl(urlparse.urlparse(uri).query, True))
        if 'redirect_uri' not in params:
            raise ReportedError('Missing parameter redirect_uri in URL query', 400)

        if 'response_type' not in params:
            raise ReportedError('Missing parameter response_type in URL query', 302, params['redirect_uri'])

        if 'client_id' not in params:
            raise ReportedError('Missing parameter client_id in URL query', 302, params['redirect_uri'])

        return self.get_authorization_code(**params)

    def get_token_from_post_data(self, data):
        """Get a token response from POST data.

        :param data: POST data containing authorization information.
        :type data: dict
        :rtype: requests.Response
        """
        # Verify OAuth 2.0 Parameters
        for x in ['grant_type', 'client_id', 'client_secret']:
            if not data.get(x):
                raise TypeError("Missing required OAuth 2.0 POST param: {0}".format(x))
        
        # Handle get token from refresh_token
        if 'refresh_token' in data:
            return self.refresh_token(**data)

        # Handle get token from authorization code
        for x in ['redirect_uri', 'code']:
            if not data.get(x):
                raise TypeError("Missing required OAuth 2.0 POST param: {0}".format(x))            
        return self.get_token(**data)

    def validate_client_id(self, client_id):
        raise NotImplementedError('Subclasses must implement ' \
                                  'validate_client_id.')

    def validate_client_secret(self, client_id, client_secret):
        raise NotImplementedError('Subclasses must implement ' \
                                  'validate_client_secret.')

    def validate_redirect_uri(self, client_id, redirect_uri):
        raise NotImplementedError('Subclasses must implement ' \
                                  'validate_redirect_uri.')

    def validate_scope(self, client_id, scope):
        raise NotImplementedError('Subclasses must implement ' \
                                  'validate_scope.')

    def validate_access(self):
        raise NotImplementedError('Subclasses must implement ' \
                                  'validate_access.')

    def from_authorization_code(self, client_id, code, scope):
        raise NotImplementedError('Subclasses must implement ' \
                                  'from_authorization_code.')

    def from_refresh_token(self, client_id, refresh_token, scope):
        raise NotImplementedError('Subclasses must implement ' \
                                  'from_refresh_token.')

    def persist_authorization_code(self, client_id, code, scope):
        raise NotImplementedError('Subclasses must implement ' \
                                  'persist_authorization_code.')

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in, refresh_token,
                                  data):
        raise NotImplementedError('Subclasses must implement ' \
                                  'persist_token_information.')

    def discard_authorization_code(self, client_id, code):
        raise NotImplementedError('Subclasses must implement ' \
                                  'discard_authorization_code.')

    def discard_refresh_token(self, client_id, refresh_token):
        raise NotImplementedError('Subclasses must implement ' \
                                  'discard_refresh_token.')
