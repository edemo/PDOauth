from pdoauth.app import db

class ModelUtils(object):

    def save(self):
        session = db.session
        session.add(self)
        session.commit()
        
    def rm(self):
        session = db.session
        session.delete(self)
        session.commit()
        
