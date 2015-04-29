from app import app
from pdoauth.AuthProvider import AuthProvider
from flask_login import login_required
from pdoauth.auth import do_login
from flask.globals import request
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.User import User
from flask import json

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
    authHeader = request.headers.get('Authorization')
    if authHeader:
        token = authHeader.split(" ")[1]
        data = TokenInfoByAccessKey.find(token)
        user_id = data.tokeninfo.user_id
        user = User.get(user_id)
        data = {
            'userid': user.id,
            'name': user.username
            }
        return json.dumps(data)
    

if __name__ == '__main__':
    app.run("localhost", 8888, True)


