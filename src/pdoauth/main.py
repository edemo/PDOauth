from pdoauth.app import app, login_manager
from pdoauth.AuthProvider import AuthProvider
from pdoauth.Controller import Controller
from flask_login import login_required
from flask.helpers import send_from_directory
from pdoauth.models.User import User
import os
from flask.globals import request
from urllib import urlencode
from pdoauth.FlaskInterface import FlaskInterface

Controller.setInterface(FlaskInterface)

controller = Controller.getInstance()

@login_manager.unauthorized_handler
def unauthorized():
    resp = controller.error_response(["authentication needed"], 302)
    uri = "{1}?{0}".format(urlencode({"next": request.url}), app.config.get("START_URL"))
    resp.headers['Location'] = uri
    return resp

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.route("/v1/oauth2/auth", methods=["GET"])
@login_required
def authorization_code():
    "see http://tech.shift.com/post/39516330935/implementing-a-python-oauth-2-0-provider-part-1"
    return AuthProvider.auth_interface()

#@app.route("/login", methods=["POST"])

def login():
    return controller.do_login()

@app.route("/ssl_login", methods=["GET"])
def ssl_login():
    return controller.do_ssl_login()

@app.route("/keygen", methods=["POST"])
def keygen():
    return controller.do_keygen()

@app.route("/deregister", methods=["POST"])
def deregister():
    return controller.do_deregister()

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    return controller.do_logout()

@app.route("/v1/oauth2/token", methods=["POST"])
def token():
    return AuthProvider.token_interface()

@app.route("/v1/users/<userid>", methods=["GET"])
def showUser(userid):
    return controller.do_show_user(userid)

@app.route("/v1/users/me/change_password", methods=["POST"])
def changePassword():
    return controller.do_change_password()

@app.route("/v1/users/<email>/passwordreset", methods=["GET"])
def sendPasswordResetEmail(email):
    return controller.do_send_password_reset_email(email)

@app.route("/v1/users/me/update_hash", methods=["POST"])
@login_required
def updateHash():
    return controller.do_update_hash()

@app.route("/v1/password_reset", methods=["POST"])
def passwordReset():
    return controller.do_password_reset()

@app.route("/v1/register", methods=["POST"])
def register():
    return controller.do_registration()

@app.route("/v1/verify_email/<token>", methods=["GET"])
def verifyEmail(token):
    return controller.do_verify_email(token)

@app.route('/v1/user_by_email/<email>', methods=["GET"])
@login_required
def get_by_email(email):
    return controller.do_get_by_email(email)

@app.route('/v1/add_assurance', methods=["POST"])
@login_required
def add_assurance():
    return controller.do_add_assurance()

@app.route('/v1/add_credential', methods=["POST"])
@login_required
def add_credential():
    return controller.do_add_credential()

@app.route('/v1/remove_credential', methods=["POST"])
@login_required
def remove_credential():
    return controller.do_remove_credential()

@app.route('/uris', methods=["GET"])
def uriservice():
    return controller.do_uris()

def getStaticPath():
    mainpath = os.path.abspath(__file__)
    up = os.path.dirname
    ret = os.path.join(up(up(up(mainpath))), 'static')
    return ret

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory(getStaticPath(), path)

