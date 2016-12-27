from pdoauth.models.Application import Application
from pdoauth.models.AppMap import AppMap
import json
from pdoauth.WebInterface import WebInterface
from pdoauth.ReportedError import ReportedError
from pdoauth import Messages

class AppHandler(WebInterface):

    def createUserAppMapEntry(self, user, app):
        entry = dict(name=app.name, 
            can_email=app.can_email, 
            hostname=app.redirect_uri.split('/')[2])
        appMapEntry = AppMap.find(app, user)
        if appMapEntry:
            entry['email_enabled'] = appMapEntry.can_email
            entry['username'] = appMapEntry.userid
        else:
            entry['email_enabled'] = None
            entry['username'] = None
        return entry

    def getAppList(self, user):
        ret = list()
        for app in Application.all():
            entry = self.createUserAppMapEntry(user, app)
            ret.append(entry)
        return ret

    def getApplistAsJson(self,user):
        return json.dumps(self.getAppList(user))

    def getApplistInterFace(self):
        user = self.getCurrentUser()
        return self.getApplistAsJson(user)
    
    def setCanEmail(self, appName, user, value):
        app = Application.find(appName)
        if app == None:
            raise ReportedError(Messages.unknownApplication)
        theMap = AppMap.get(app, user)
        theMap.can_email = value
        theMap.save()

    
    def setAppCanEmail(self, form):
        user = self.getCurrentUser()
        self.setCanEmail(form.appname.data, user, form.canemail.data)
        ret = self.getApplistAsJson(user)
        return ret
    
    

    
    
