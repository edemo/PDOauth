from app import app
from pdoauth.AuthProvider import AuthProvider
from flask_login import login_required, current_user
from pdoauth.auth import do_login, do_registration
from flask.globals import request
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.User import User
from flask import json
import flask

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

def isAllowedToGetUser(userid):
    allowed = False
    authuser = None
    authHeader = request.headers.get('Authorization')
    if current_user.is_authenticated():
        if userid == 'me':
            return (True,current_user)
    if authHeader:
        token = authHeader.split(" ")[1]
        data = TokenInfoByAccessKey.find(token)
        targetuserid = data.tokeninfo.user_id
        authuser = User.get(targetuserid)
        allowed = authuser.id == userid or userid == 'me'
    return allowed, authuser

@app.route("/v1/users/<userid>", methods=["GET"])
def showUser(userid):
    allowed, targetuser = isAllowedToGetUser(userid)
    if allowed:
        data = {
                'email': targetuser.email,
                'userid': targetuser.id
                }
        return json.dumps(data)
    return flask.make_response("no authorization", 403)

@app.route("/v1/register", methods=["POST"])
def register():
    return do_registration()

if __name__ == '__main__':
    app.run("localhost", 8888, True)


