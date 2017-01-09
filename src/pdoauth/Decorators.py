from pdoauth.ReportedError import ReportedError
from pdoauth.WebInterface import WebInterface
from pdoauth.Responses import Responses
import sys
from pdoauth.app import app
import traceback

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
            resp = func(*args, **kwargs)
        except ReportedError as e:
            resp = self.errorReport(e)
        if "noheaders" == getattr(resp,"headers","noheaders"):
            resp = self.make_response(resp, 200)
        resp.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
        resp.headers['Pragma'] = "no-cache"
        resp.headers['Expires'] = "0"
        return resp

    @staticmethod
    def getRaisePoint():
        exc_type, exc_value, exc_traceback = sys.exc_info() # @UnusedVariable
        l = traceback.extract_tb(exc_traceback)[-1]
        raisedAt = traceback.format_list([l])[0]
        return raisedAt

    def errorReport(self, e):
        raisedAt = self.getRaisePoint()
        app.logger.info("status={0}, descriptor={1}, raised at={2}".format(e.status, e.descriptor, raisedAt))
        if e.status == 302:
            response = self.makeJsonResponse(dict(errors=e.descriptor), e.status)
            response.headers['Location'] = '{0}?errors={1}'.format(e.uri,e.descriptor)
            return response
        resp = self.error_response(e.descriptor, e.status)
        resp.headers['Access-Control-Allow-Origin'] = self.app.config.get('BASE_URL')
        return resp

    def interfaceFunc(self, rule, formClass=None, status=400, checkLoginFunction=None, **options):
        def DECORATOR(func):
            def validated(*args, **kwargs):
                return self.runInterfaceFunc(func, args, kwargs, formClass, status, checkLoginFunction)
            validated.__name__ = func.__name__
            endpoint = options.pop('endpoint', None)
            self.app.add_url_rule(rule, endpoint, validated, **options)
            return validated
        return DECORATOR
