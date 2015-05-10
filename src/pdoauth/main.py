from pdoauth.app import app, login_manager
from pdoauth.AuthProvider import AuthProvider
from pdoauth.auth import do_login, do_registration, do_get_by_email,\
    do_add_assurance, do_show_user, do_verify_email, error_response,\
    do_change_password
from flask_login import login_required
from flask.helpers import send_from_directory
from pdoauth.models.User import User
import os


@login_manager.unauthorized_handler
def unauthorized():
    resp = error_response(["authentication needed"], 302)
    resp.headers['Location'] = '/static/login.html'
    return resp

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

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

@app.route("/v1/users/<userid>/change_password", methods=["POST"])
def changePassword(userid):
    return do_change_password(userid)

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

def getStaticPath():
    mainpath = os.path.abspath(__file__)
    up = os.path.dirname
    ret = os.path.join(up(up(up(mainpath))), 'static')
    return ret

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(getStaticPath(), path)

if __name__ == '__main__':
    app.run("localhost", 8888)
