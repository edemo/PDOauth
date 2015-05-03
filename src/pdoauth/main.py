from app import app
from pdoauth.AuthProvider import AuthProvider
from flask_login import login_required, login_user, current_user
from pdoauth.auth import do_login
from flask.globals import request
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.User import User
from flask import json
from pdoauth.CredentialManager import CredentialManager
from flask.helpers import flash
from werkzeug import redirect
from pdoauth.forms.RegistrationForm import RegistrationForm
from flask.templating import render_template
from pdoauth.forms.LoginForm import LoginForm
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
                'name': targetuser.username,
                'userid': targetuser.id
                }
        return json.dumps(data)
    return flask.make_response("no authorization", 403)

@app.route("/v1/register", methods=["POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = CredentialManager.create_from_form(form)
        if user is None:
            return render_template("login.html", regform=form, form=LoginForm())
        user.set_authenticated()
        user.activate()
        r = login_user(user)
        if r:
            flash("registeread and logged in successfully.")
            return redirect(request.form.get("next") or "/")
    return render_template("login.html", regform=form, form=LoginForm())

if __name__ == '__main__':
    app.run("localhost", 8888, True)


