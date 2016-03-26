
class Observable(object):
    observers = None
    @classmethod
    def subscribe(cls,observerfunct,event):
        if cls.observers is None:
            cls.observers = dict()
        if not event in cls.observers:
            cls.observers[event]=list()
        cls.observers[event].append(observerfunct)

    def notify(self, event):
        if self.observers is None:
            return
        handlers = self.__class__.observers[event]
        for handler in handlers:
            handler(self)
