from app import app
from pdoauth.AuthProvider import AuthProvider
from flask_login import login_required
from pdoauth.auth import do_login
from flask.globals import request
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey

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
    print "header:{0}".format(authHeader)
    if authHeader:
        token = authHeader.split(" ")[1]
        print "token:{0}".format(token)
        data = TokenInfoByAccessKey.find(token)
        print "data:{0}".format(data)
        return token
    

if __name__ == '__main__':
    app.run("localhost", 8888, True)


