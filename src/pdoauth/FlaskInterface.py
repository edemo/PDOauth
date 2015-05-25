from pdoauth.models.Assurance import Assurance
from pdoauth.models.Credential import Credential
from flask import json
import urllib3
import flask

class FlaskInterface(object):
    @classmethod
    def make_response(self, ret, status):
        return flask.make_response(ret, status)
    
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
    def exceptionChecked(cls,func):
        def f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ReportedError as e:
                return cls.error_response(e.descriptor, e.status)         
        return f

    @classmethod
    def _make_response(self, descriptor,status=200):
        ret = json.dumps(descriptor)
        return self.make_response(ret, status)
    
    @classmethod
    def error_response(self,descriptor, status=400):
        return self._make_response(dict(errors=descriptor), status)

class ReportedError(Exception):
    def __init__(self, descriptor, status=400):
        self.descriptor = descriptor
        self.status = status


class Responses(object):

    def errors_to_json(self, form):
        errs = []
        for field, errors in form.errors.items():
            for error in errors:
                fieldname = getattr(form, field).label.text
                errs.append("{0}: {1}".format(fieldname,error))
        return errs

    def simple_response(self,text):
        return self._make_response(dict(message=text))
    
    def form_validation_error_response(self, form, status=400):
        errdict = self.errors_to_json(form)
        return self.error_response(errdict, status)
    
    def as_dict(self, user, **kwargs):
        kwargs.update({'email':user.email, 
            'userid':user.userid, 
            'assurances':Assurance.getByUser(user),
            'credentials': Credential.getByUser_as_dictlist(user)
        })
        ret = json.dumps(kwargs)
        return self.make_response(ret,200)
