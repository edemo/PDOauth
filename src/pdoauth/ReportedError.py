
class ReportedError(Exception):
    def __init__(self, descriptor, status=400):
        self.descriptor = descriptor
        self.status = status
