from pdoauth.models.Assurance import Assurance
from pdoauth.models.Credential import Credential
from flask import json
import urlparse
import urllib
class Responses(object):

    def errors_to_json(self, form):
        errs = []
        for field, errors in form.errors.items():
            for error in errors:
                fieldname = getattr(form, field).label.text
                errs.append("{0}: {1}".format(fieldname,error))
        return errs

    def simple_response(self,text,additionalInfo=None):
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
        ret = json.dumps(kwargs)
        return self.make_response(ret,200)

    def makeJsonResponse(self, descriptor,status=200):
        ret = json.dumps(descriptor)
        return self.make_response(ret, status)
    
    def error_response(self,descriptor, status=400):
        return self.makeJsonResponse(dict(errors=descriptor), status)

    def form_validation_error_response(self, form, status=400):
        errdict = self.errors_to_json(form)
        return self.error_response(errdict, status)

    def build_url(self, base, additional_params=None):
        url = urlparse.urlparse(base)
        query_params = {}
        query_params.update(urlparse.parse_qsl(url.query, True))
        if additional_params is not None:
            query_params.update(additional_params)
            for k, v in additional_params.iteritems():
                if v is None:
                    query_params.pop(k)
    
        return urlparse.urlunparse((url.scheme,
                                    url.netloc,
                                    url.path,
                                    url.params,
                                    urllib.urlencode(query_params),
                                    url.fragment))

    def getParamsOfUri(self, uri):
        params = dict(urlparse.parse_qsl(urlparse.urlparse(uri).query, True))
        return params

