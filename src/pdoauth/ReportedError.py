
class ReportedError(Exception):
    def __init__(self, descriptor, status=400, uri=None):
        self.descriptor = descriptor
        self.status = status
        if status == 302 and uri is None:
            raise Exception('302 without uri')
        self.uri = uri
