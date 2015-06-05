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
            validated.func_name = func.func_name
            return validated
        return decorator

    @classmethod
    def runWithExceptionCheck(cls, func, args, kwargs):
            try:
                return func(*args, **kwargs)
            except ReportedError as e:
                resp = cls.errorReport(e)
                return resp
    @classmethod
    def exceptionChecked(cls,func):
        def _f(*args, **kwargs):
            return cls.runWithExceptionCheck(func, args, kwargs)
        _f.func_name = func.func_name 
        return _f

    @classmethod
    def setAuthUser(cls, userid, isHerself):
        cls.getSession()['auth_user']=(userid, isHerself)

    @classmethod
    def authenticateUserOrBearer(cls):
        authHeader = cls.getHeader('Authorization')
        current_user = cls.getCurrentUser()
        if current_user.is_authenticated():
            cls.setAuthUser(current_user.userid, True)
        elif authHeader:
            token = authHeader.split(" ")[1]
            data = TokenInfoByAccessKey.find(token)
            targetuserid = data.tokeninfo.user_id
            cls.setAuthUser(targetuserid, False)
        else:
            raise ReportedError(["no authorization"], status=403)

    @classmethod
    def runInterfaceFunc(cls, func, args, kwargs, formClass, status, checkLoginFunction):
        if checkLoginFunction is not None:
            unauthorized = checkLoginFunction()
            if unauthorized:
                return unauthorized
        try:
            if formClass is not None:
                form = formClass()
                if not form.validate_on_submit():
                    return cls.form_validation_error_response(form, status)
                kwargs["form"] = form
            return func(*args, **kwargs)
        except ReportedError as e:
            resp = cls.errorReport(e)
            return resp
    @classmethod
    def errorReport(cls, e):
        logging.log(logging.INFO, "status={0}, descriptor={1}".format(e.status, e.descriptor))
        resp = cls.error_response(e.descriptor, e.status)
        resp.headers['Access-Control-Allow-Origin'] = cls.app.config.get('BASE_URL')
        return resp

    @classmethod
    def interfaceFunc(cls, rule, formClass=None, status=400, checkLoginFunction=None, **options):
        def decorator(func):
            def validated(*args, **kwargs):
                return cls.runInterfaceFunc(func, args, kwargs, formClass, status, checkLoginFunction)
            validated.func_name = func.func_name
            endpoint = options.pop('endpoint', None)
            cls.app.add_url_rule(rule, endpoint, validated, **options)
            return validated
        return decorator

    
    @classmethod
    def checkLogin(cls):
        if not cls.getCurrentUser().is_authenticated():
            return cls.app.login_manager.unauthorized()
    
    

