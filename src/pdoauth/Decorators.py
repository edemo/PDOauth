from pdoauth.ReportedError import ReportedError
from pdoauth.WebInterface import WebInterface
import logging
from pdoauth.Responses import Responses

class Decorators(WebInterface, Responses):
    def __init__(self, app, interface):
        self.app = app
        WebInterface.__init__(self, interface)

    def runInterfaceFunc(self, func, args, kwargs, formClass, status, checkLoginFunction):
        try:
            if checkLoginFunction is not None:
                unauthorized = checkLoginFunction()
                if unauthorized:
                    return unauthorized
            if formClass is not None:
                form = formClass()
                if not form.validate_on_submit():
                    return self.form_validation_error_response(form, status)
                kwargs["form"] = form
            return func(*args, **kwargs)
        except ReportedError as e:
            resp = self.errorReport(e)
            return resp

    def errorReport(self, e):
        logging.log(logging.INFO, "status={0}, descriptor={1}".format(e.status, e.descriptor))
        resp = self.error_response(e.descriptor, e.status)
        resp.headers['Access-Control-Allow-Origin'] = self.app.config.get('BASE_URL')
        return resp

    def interfaceFunc(self, rule, formClass=None, status=400, checkLoginFunction=None, **options):
        def DECORATOR(func):
            def validated(*args, **kwargs):
                return self.runInterfaceFunc(func, args, kwargs, formClass, status, checkLoginFunction)
            validated.func_name = func.func_name
            endpoint = options.pop('endpoint', None)
            self.app.add_url_rule(rule, endpoint, validated, **options)
            return validated
        return DECORATOR
