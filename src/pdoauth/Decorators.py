from pdoauth.ReportedError import ReportedError
from pdoauth.models.Assurance import Assurance
from pdoauth.models.User import User
from pdoauth.models.TokenInfoByAccessKey import TokenInfoByAccessKey
from pdoauth.Interfaced import Interfaced

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

