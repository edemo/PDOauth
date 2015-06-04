from pdoauth.models.Assurance import Assurance
from pdoauth.models.Credential import Credential
from flask import json
import urllib3
import flask
from pdoauth.app import app, logging
from pdoauth.ReportedError import ReportedError
from flask.globals import session, request
from flask_login import login_user, current_user

class Responses(object):

    @classmethod
    def errors_to_json(self, form):
        errs = []
        for field, errors in form.errors.items():
            for error in errors:
                fieldname = getattr(form, field).label.text
                errs.append("{0}: {1}".format(fieldname,error))
        return errs

    def simple_response(self,text):
        return self._make_response(dict(message=text))
    
    def as_dict(self, user, **kwargs):
        kwargs.update({'email':user.email, 
            'userid':user.userid, 
            'assurances':Assurance.getByUser(user),
            'hash': user.hash,
            'credentials': Credential.getByUser_as_dictlist(user)
        })
        ret = json.dumps(kwargs)
        return self.make_response(ret,200)

    @classmethod
    def _make_response(self, descriptor,status=200):
        ret = json.dumps(descriptor)
        return self.make_response(ret, status)
    
    @classmethod
    def error_response(self,descriptor, status=400):
        return self._make_response(dict(errors=descriptor), status)

    @classmethod
    def form_validation_error_response(self, form, status=400):
        errdict = self.errors_to_json(form)
        return self.error_response(errdict, status)
    
    @classmethod
    def make_response(self, ret, status):
        return flask.make_response(ret, status)

class Decorators(object):
    @classmethod
    def formValidated(cls, formClass, status=400):
        def decorator(func):
            def validated(*args,**kwargs):
                form = formClass()
                kwargs['form']=form
                if form.validate_on_submit():
                    return func(*args, **kwargs)
                return cls.form_validation_error_response(form, status)
            return validated
        return decorator

    @classmethod
    def exceptionChecked(cls,func):
        def _f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ReportedError as e:
                resp = cls.errorReport(e)
                return resp      
        return _f


class FlaskInterface(Responses, Decorators):
    
    def getHeader(self, header):
        return request.headers.get(header)

    def getCurrentUser(self):
        return current_user

    def getEnvironmentVariable(self, variableName):
        return request.environ.get(variableName, None)

    @classmethod
    def getRequestForm(self):
        return request.form

    @classmethod
    def getRequestUrl(self):
        return request.url

    def validate_on_submit(self,form):
        return form.validate_on_submit()

    def _facebookMe(self, code):
        args = {"access_token":code, 
            "format":"json", 
            "method":"get"}
        http = urllib3.PoolManager()
        resp = http.request('GET', "https://graph.facebook.com/v2.2/me", args)
        return resp

    @classmethod
    def interfaceFunc(cls, rule, formClass=None, status=400, **options):
        def decorator(func):
            def validated(*args, **kwargs):
                if formClass is not None:
                    form = formClass()
                    if not form.validate_on_submit():
                        return cls.form_validation_error_response(form, status)
                    kwargs["form"] = form
                try:
                    return func(*args, **kwargs)
                except ReportedError as e:
                    resp = cls.errorReport(e)
                    return resp
            endpoint = options.pop('endpoint', None)
            app.add_url_rule(rule, endpoint, validated, **options)
            return validated
        return decorator

    @classmethod
    def errorReport(cls, e):
        logging.log(logging.INFO, "status={0}, descriptor={1}".format(e.status, e.descriptor))
        resp = cls.error_response(e.descriptor, e.status)
        resp.headers['Access-Control-Allow-Origin'] = app.config.get('BASE_URL')
        return resp

    def getSession(self):
        return session

    def loginUserInFramework(self, user):
        r = login_user(user)
        return r
