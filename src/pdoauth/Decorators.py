from pdoauth.ReportedError import ReportedError
from pdoauth.models.Assurance import Assurance
from pdoauth.models.User import User
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.Interfaced import Interfaced
import logging

class Decorators(Interfaced):
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

    @classmethod
    def authenticateUserOrBearer(cls, func):
        def _f(self, userid):
            authHeader = cls.getHeader('Authorization')
            current_user = cls.getCurrentUser()
            if current_user.is_authenticated():
                if userid == 'me':
                    authuser = current_user
                elif Assurance.getByUser(current_user).has_key('assurer'):
                    authuser = User.get(userid)
                else:
                    raise ReportedError(["no authorization to show other users"], status=403)
            elif authHeader:
                token = authHeader.split(" ")[1]
                data = TokenInfoByAccessKey.find(token)
                targetuserid = data.tokeninfo.user_id
                authuser = User.get(targetuserid)
                if not (authuser.id == userid or userid == 'me'):
                    raise ReportedError(["bad bearer authentication"], status=403)
            else:
                raise ReportedError(["no authorization"], status=403)
            return func(self, authuser)
        return _f

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
            cls.app.add_url_rule(rule, endpoint, validated, **options)
            return validated
        return decorator

    @classmethod
    def errorReport(cls, e):
        logging.log(logging.INFO, "status={0}, descriptor={1}".format(e.status, e.descriptor))
        resp = cls.error_response(e.descriptor, e.status)
        resp.headers['Access-Control-Allow-Origin'] = cls.app.config.get('BASE_URL')
        return resp
