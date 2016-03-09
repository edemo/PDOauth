from pdoauth.models.Application import Application
from pdoauth.models.AppMap import AppMap
import json

class UserAppEntry(object):
    def __init__(self,app,user):
        self.name = app.name
        self.can_email = app.can_email
        self.hostname = app.redirect_uri.split('/')[2]
        appMapEntry =AppMap.find(app, user)
        if appMapEntry:
            self.email_enabled = appMapEntry.can_email
            self.username = appMapEntry.userid
        else:
            self.email_enabled = None
            self.username = None
    def __repr__(self):
        d = dict()
        for field in ["name", "can_email", "hostname", "email_enabled", "username"]:
            d[field] = getattr(self,field)
        return json.dumps(d)

class AppHandler(object):
    def getAppList(self, user):
        ret = list()
        for app in Application.all():
            ret.append(UserAppEntry(app,user))
        return ret
