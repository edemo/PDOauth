import time

class OnlyEmptyScopeIsAllowed(Exception):
    pass


class Authorisation(object):
    store = {}
    
    @classmethod
    def new(klass, client_id, code, scope, _called_at = None):
        return klass(client_id, code, scope, _called_at = _called_at)
    
    @staticmethod
    def getCallTime(_called_at):
        if _called_at is None:
            _called_at = time.time()
        return _called_at

    @classmethod
    def isExpired(klass, _called_at, auth):
        _called_at = klass.getCallTime(_called_at)
        return auth.created + 60 <= _called_at

    @classmethod
    def get(klass, client_id, code, _called_at = None):
        auth = klass.store[(client_id,code)]
        if klass.isExpired(_called_at, auth):
            return None
        return auth
    

    def checkScope(self, scope):
        if scope != "":
            raise OnlyEmptyScopeIsAllowed()

    def __init__(self, client_id, code, scope, _called_at = None):
        self.checkScope(scope)
        _called_at = self.getCallTime(_called_at)
        self.client_id = client_id
        self.code = code
        self.created = _called_at
        self.store[(client_id,code)] = self
