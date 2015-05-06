from app import app
from pdoauth.AuthProvider import AuthProvider
from flask_login import login_required
from pdoauth.auth import do_login, do_registration
from flask import json
import flask
from pdoauth import auth
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance

@app.route("/v1/oauth2/auth", methods=["GET"])
@login_required
def authorization_code():
    return AuthProvider.auth_interface()

@app.route("/login", methods=["GET", "POST"])
def login():
    return do_login()

@app.route("/v1/oauth2/token", methods=["POST"])
def token():
    return AuthProvider.token_interface()

@app.route("/v1/users/<userid>", methods=["GET"])
def showUser(userid):
    allowed, targetuser = auth.isAllowedToGetUser(userid)
    if allowed:
        data = {
                'email': targetuser.email,
                'userid': targetuser.id,
                'assurances': Assurance.getByUser(targetuser)
                }
        return json.dumps(data)
    return flask.make_response("no authorization", 403)

@app.route("/v1/register", methods=["POST"])
def register():
    return do_registration()

@app.route("/v1/verify_email/<token>", methods=["GET"])
def verifyEmail(token):
    cred = Credential.get('emailcheck', token)
    #assurance = Assurance.new(cred.user,'automatic', time.time())
    cred.rm()
    if cred is not None:
        return flask.make_response("email verified OK", 200)
    return flask.make_response("unknown token", 404)

if __name__ == '__main__':
    app.run("localhost", 8888, True)


