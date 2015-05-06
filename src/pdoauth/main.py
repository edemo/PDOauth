from app import app
from pdoauth.AuthProvider import AuthProvider
from pdoauth.auth import do_login, do_registration, do_get_by_email,\
    do_add_assurance, do_show_user, do_verify_email
from flask import json
import flask
from pdoauth import auth
from pdoauth.models.Credential import Credential
from pdoauth.models.Assurance import Assurance
from flask_login import login_required

@app.route("/v1/oauth2/auth", methods=["GET"])
@login_required
def authorization_code():
    return AuthProvider.auth_interface()

@app.route("/login", methods=["POST"])
def login():
    return do_login()

@app.route("/v1/oauth2/token", methods=["POST"])
def token():
    return AuthProvider.token_interface()

@app.route("/v1/users/<userid>", methods=["GET"])
def showUser(userid):
    return do_show_user(userid)

@app.route("/v1/register", methods=["POST"])
def register():
    return do_registration()

@app.route("/v1/verify_email/<token>", methods=["GET"])
def verifyEmail(token):
    return do_verify_email(token)

@app.route('/v1/user_by_email/<email>', methods=["GET"])
@login_required
def get_by_email(email):
    return do_get_by_email(email)

@app.route('/v1/add_assurance', methods=["POST"])
@login_required
def add_assurance():
    return do_add_assurance()
    
if __name__ == '__main__':
    app.run("localhost", 8888, True)


