from app import app
from pdoauth import AuthProvider
import flask
from flask.globals import request, session
from functools import wraps

def authenticate():
    resp = flask.make_response("authentication needed", 302)
    resp.headers['Location'] = '/loginpage'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(session, 'user', None) is None:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/v1/oauth2/auth", methods=["GET"])
@requires_auth
def authorization_code():
    provider = AuthProvider
    response = provider.get_authorization_code_from_uri(request.url)
    flask_res = flask.make_response(response.text, response.status_code)
    #for k, v in response.headers.iteritems():
    #    flask_res.headers[k] = v
    return flask_res

if __name__ == '__main__':
    app.run("localhost", 8888, True)


