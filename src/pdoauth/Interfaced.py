from pdoauth.FlaskInterface import FlaskInterface
class Dummy(object):
    pass
class Interfaced(FlaskInterface, Dummy):
    @classmethod
    def setInterface(cls, interface):
        bases = set(cls.__bases__)
        bases.add(interface)
        cls.__bases__ = tuple(bases)

    @classmethod
    def unsetInterface(cls, interface):
        bases = list(cls.__bases__)
        if interface in bases:
            bases.remove(interface)
        cls.__bases__ = tuple(bases)

    @classmethod
    def getInstance(cls):
        instance = getattr(cls, "instance", None)
        if instance is None:
            instance = cls()
            cls.instance = instance
        return instance

