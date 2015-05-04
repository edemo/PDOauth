from pdoauth.app import login_manager, mail, app
import flask
from pdoauth.models.User import User
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.CredentialManager import CredentialManager
from flask.helpers import flash
from flask.templating import render_template
from flask_login import login_user
from werkzeug.utils import redirect
from flask.globals import request
from pdoauth.forms.RegistrationForm import RegistrationForm
from pdoauth.models.Credential import Credential
from uuid import uuid4
import time

@login_manager.unauthorized_handler
def unauthorized():
    resp = flask.make_response("authentication needed", 302)
    resp.headers['Location'] = '/login'
    return resp

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = CredentialManager.validate_from_form(form)
        if user is None:
            flash("Bad username or password")
            return render_template("login.html", form=form, regform=RegistrationForm())
        user.set_authenticated()
        r = login_user(user)
        if r:
            return redirect(request.form.get("next") or "/")
    return render_template("login.html", form=form, regform=RegistrationForm())


def email_verification(user):
    secret=unicode(uuid4())
    expiry = time.time()
    Credential.new(user, 'emailcheck', unicode(expiry), secret)
    timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
    uri = "https://{0}/verify_email/{1}".format(app.config.get('SERVER_NAME'),secret)
    text = """Hi, click on <a href="{0}">{0}</a> until {1} to verify your email""".format(uri, timeText)
    print "sending\n{0}".format(text)
    mail.send_message(subject="verification", body=text, recipients=[user.email], sender="FIXME@FIXME.FIXME")

def do_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = CredentialManager.create_from_form(form)
        if user is None:
            flash("There is already a user with that email: {0.email.data}".format(form))
            return render_template("login.html", regform=form, form=LoginForm())
        email_verification(user)
        user.set_authenticated()
        user.activate()
        r = login_user(user)
        if r:
            flash("registeread and logged in successfully.")
            return redirect(request.form.get("next") or "/")
    return render_template("login.html", regform=form, form=LoginForm())
