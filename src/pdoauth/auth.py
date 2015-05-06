from pdoauth.app import login_manager, mail, app
import flask
from pdoauth.models.User import User
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.CredentialManager import CredentialManager
from flask.helpers import flash
from flask.templating import render_template
from flask_login import login_user, current_user
from werkzeug.utils import redirect
from flask.globals import request
from pdoauth.forms.RegistrationForm import RegistrationForm
from pdoauth.models.Credential import Credential
from uuid import uuid4
import time
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.Assurance import Assurance
from pdoauth.forms.AssuranceForm import AssuranceForm

@login_manager.unauthorized_handler
def unauthorized():
    resp = flask.make_response("authentication needed", 302)
    resp.headers['Location'] = '/login'
    return resp

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

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
        flash("Inactive or disabled user")
    flash_errors(form)
    return render_template("login.html", form=form, regform=RegistrationForm())


def email_verification(user):
    secret=unicode(uuid4())
    expiry = time.time()
    Credential.new(user, 'emailcheck', secret, unicode(expiry))
    timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
    uri = "https://{0}/v1/verify_email/{1}".format(app.config.get('SERVER_NAME'),secret)
    text = """Hi, click on <a href="{0}">{0}</a> until {1} to verify your email""".format(uri, timeText)
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

def isAllowedToGetUser(userid):
    allowed = False
    authuser = None
    authHeader = request.headers.get('Authorization')
    if current_user.is_authenticated():
        if userid == 'me':
            return (True,current_user)
        if Assurance.getByUser(current_user).has_key('assurer'):
            authuser = User.get(userid)
            return (True, authuser)
    if authHeader:
        token = authHeader.split(" ")[1]
        data = TokenInfoByAccessKey.find(token)
        targetuserid = data.tokeninfo.user_id
        authuser = User.get(targetuserid)
        allowed = authuser.id == userid or userid == 'me'
    return allowed, authuser

def do_get_by_email(email):
    assurances = Assurance.getByUser(current_user)
    if assurances.has_key('assurer'):
        user = User.getByEmail(email)
        return redirect("/v1/users/{0}".format(user.id))
    return flask.make_response("no authorization", 403)


def do_add_assurance():
    form = AssuranceForm()
    if form.validate_on_submit():
        assurances = Assurance.getByUser(current_user)
        neededAssurance = form.assurance.data
        assurerAssurance = "assurer.{0}".format(neededAssurance)
        if assurances.has_key('assurer') and assurances.has_key(assurerAssurance):
            user = User.getByEmail(form.email.data)
            Assurance.new(user, neededAssurance, current_user)
            responseText = "added assurance {0} to user {1}".format(neededAssurance, user.email)
            return flask.make_response(responseText, 200)
        return flask.make_response("no authorization", 403)
    flash_errors(form)
    return render_template("add_assurance.html", form=form)
