from pdoauth.app import db
from pdoauth.Observable import Observable

class ModelUtils(Observable):

    def save(self):
        session = db.session
        session.add(self)
        session.commit()
        
    def rm(self):
        self.notify("pre_rm")
        session = db.session
        session.delete(self)
        session.commit()

    @classmethod
    def getStats(klass):
        return klass.query.count()
        
