from pdoauth.app import mail, app
import flask
from pdoauth.models.User import User
from pdoauth.forms.LoginForm import LoginForm
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user, current_user
from flask.globals import request, session
from pdoauth.forms.RegistrationForm import RegistrationForm
from pdoauth.models.Credential import Credential
from uuid import uuid4
import time
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.models.Assurance import Assurance
from pdoauth.forms.AssuranceForm import AssuranceForm
from flask import json
from pdoauth.forms.PasswordChangeForm import PasswordChangeForm


def errors_to_json(form):
    errs = []
    for field, errors in form.errors.items():
        for error in errors:
            fieldname = getattr(form, field).label.text
            errs.append("{0}: {1}".format(fieldname,error))
    return errs

def _make_response(descriptor,status=200):
    ret = json.dumps(descriptor)
    return flask.make_response(ret, status)

def simple_response(text):
    return _make_response(dict(message=text))

def error_response(descriptor, status=400):
    return _make_response(dict(errors=descriptor), status)

def form_validation_error_response(form, status=400):
    errdict = errors_to_json(form)
    return error_response(errdict, status)

    
def as_dict(user):
    data = {'email':user.email, 
        'userid':user.id, 
        'assurances':Assurance.getByUser(user)}
    ret = json.dumps(data)
    return flask.make_response(ret,200)

def email_verification(user):
    secret=unicode(uuid4())
    expiry = time.time()
    Credential.new(user, 'emailcheck', secret, unicode(expiry))
    timeText = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(expiry))
    uri = "https://{0}/v1/verify_email/{1}".format(app.config.get('SERVER_NAME'),secret)
    text = """Hi, click on <a href="{0}">{0}</a> until {1} to verify your email""".format(uri, timeText)
    mail.send_message(subject="verification", body=text, recipients=[user.email], sender=app.config.get('SERVER_EMAIL_ADDRESS'))

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

def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = CredentialManager.validate_from_form(form)
        if user is None:
            return error_response(["Bad username or password"], status=403)
        user.set_authenticated()
        r = login_user(user)
        if r:
            resp = as_dict(user)
            token = unicode(uuid4())
            session['csrf_token'] = token
            resp.set_cookie("csrf",token)
            return resp
        return error_response(["Inactive or disabled user"], status=403)
    return form_validation_error_response(form, status=403)


def do_registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = CredentialManager.create_from_form(form)
        if user is None:
            return error_response(["There is already a user with that username or email", form.email.data])
        email_verification(user)
        user.set_authenticated()
        user.activate()
        r = login_user(user)
        if r:
            return as_dict(user)
    return form_validation_error_response(form)

def do_change_password(userid):
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if userid == 'me':
            user = current_user
        else:
            user = User.get(userid)
        cred = Credential.getByUser(user, 'password')
        oldSecret = CredentialManager.protect_secret(form.oldPassword.data)
        if cred.secret != oldSecret:
            return error_response(["old password does not match"])
        secret = CredentialManager.protect_secret(form.newPassword.data)
        cred.secret = secret
        cred.save()
        return simple_response('pasword changed succesfully')
    return form_validation_error_response(form)

def do_get_by_email(email):
    assurances = Assurance.getByUser(current_user)
    if assurances.has_key('assurer'):
        user = User.getByEmail(email)
        if user is None:
            return error_response(["no such user"], status=404)
        return as_dict(user)
    return error_response(["no authorization"], status=403)

def do_add_assurance():
    form = AssuranceForm()
    if form.validate_on_submit():
        assurances = Assurance.getByUser(current_user)
        neededAssurance = form.assurance.data
        assurerAssurance = "assurer.{0}".format(neededAssurance)
        if assurances.has_key('assurer') and assurances.has_key(assurerAssurance):
            user = User.getByEmail(form.email.data)
            Assurance.new(user, neededAssurance, current_user)
            return simple_response("added assurance {0} for {1}".format(neededAssurance, user.email))
        return error_response(["no authorization"], 403)
    return form_validation_error_response(form)


def do_show_user(userid):
    allowed, targetuser = isAllowedToGetUser(userid)
    if allowed:
        return as_dict(targetuser)
    return error_response(["no authorization"], status=403)

def do_verify_email(token):
    cred = Credential.get('emailcheck', token)
    if cred is None:
        return error_response(["unknown token"], 404)
    user = cred.user
    Assurance.new(user,'emailverification',user)
    cred.rm()
    return simple_response("email verified OK")
 
