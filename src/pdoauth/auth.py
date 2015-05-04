from pdoauth.app import login_manager
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

def do_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = CredentialManager.create_from_form(form)
        if user is None:
            flash("There is already a user with that email: {0.email.data}".format(form))
            return render_template("login.html", regform=form, form=LoginForm())
        user.set_authenticated()
        user.activate()
        r = login_user(user)
        if r:
            flash("registeread and logged in successfully.")
            return redirect(request.form.get("next") or "/")
    return render_template("login.html", regform=form, form=LoginForm())
