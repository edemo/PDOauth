from pdoauth.models.Assurance import Assurance
from pdoauth.models.Credential import Credential
from flask import json
import uritools
from typing import Union, List

I18ableMessage = List[str]
I18ableMessages = Union[str,List[I18ableMessage]]

class Responses(object):

    def errors_to_json(self, form):
        errs = []
        for field, errors in form.errors.items():
            for error in errors:
                fieldname = getattr(form, field).label.text
                errs.append("{0}: {1}".format(fieldname,error))
        return errs

    def simple_response(self, text, additionalInfo:dict = None):
        #text: I18ableMessages https://github.com/RussBaz/enforce/issues/31
        if additionalInfo is None:
            additionalInfo = dict()
        additionalInfo['message']=text
        return self.makeJsonResponse(additionalInfo)

    def addUserDataToDict(self, user, kwargs):
        return kwargs.update({'email':user.email, 'userid':user.userid,
                'assurances':Assurance.getByUser(user),
                'hash':user.hash,
                'credentials':Credential.getByUser_as_dictlist(user)})

    def as_dict(self, user, **kwargs):
        self.addUserDataToDict(user, kwargs)
        return self.makeJsonResponse(kwargs, 200)

    def makeJsonResponse(self, descriptor,status=200):
        ret = json.dumps(descriptor)
        return self.make_response(ret, status)
    
    def error_response(self,descriptor, status=400):
        return self.makeJsonResponse(dict(errors=descriptor), status)

    def form_validation_error_response(self, form, status=400):
        errdict = self.errors_to_json(form)
        return self.error_response(errdict, status)

    def getParamsOfUri(self, url):
        parts = uritools.urisplit(url)
        return parts.getquerydict()
    
    @classmethod
    def build_url(cls, base, additional_params=None):
        url = uritools.urisplit(base)
        query_params = url.getquerydict()
        if additional_params is not None:
            query_params.update(additional_params)
            for k, v in additional_params.items():
                if v is None:
                    query_params.pop(k)
        return uritools.uricompose(scheme=url.scheme,
                                    host=url.host,
                                    port=url.port,
                                    path=url.path,
                                    query=query_params,
                                    fragment=url.fragment)

