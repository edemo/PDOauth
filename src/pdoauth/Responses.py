from pdoauth.models.Assurance import Assurance
from pdoauth.models.Credential import Credential
from flask import json
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
        return self.makeJsonResponse(dict(message=text))
    
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
    def makeJsonResponse(self, descriptor,status=200):
        ret = json.dumps(descriptor)
        return self.make_response(ret, status)
    
    @classmethod
    def error_response(self,descriptor, status=400):
        return self.makeJsonResponse(dict(errors=descriptor), status)

    @classmethod
    def form_validation_error_response(self, form, status=400):
        errdict = self.errors_to_json(form)
        return self.error_response(errdict, status)
    
