from pdoauth.AppHandler import AppHandler
import random
from test.helpers.FakeInterFace import FakeInterface
from test.helpers.AuthProviderUtil import AuthProviderUtil
from test.helpers.PDUnitTest import PDUnitTest
from test.helpers.UserUtil import UserUtil
from pdoauth.models.Application import Application
from pdoauth.models.AppMap import AppMap

class AppInfoUtil(PDUnitTest, UserUtil, AuthProviderUtil):

    @classmethod
    def setUpClass(klass):
        klass.util=UserUtil()
        klass.user = klass.util.createUserWithCredentials().user
        klass.user.username = klass.util.userCreationUserid
        klass.user.password = klass.util.usercreationPassword
        klass.createTestAppMaps()
        klass.appHandler = AppHandler(FakeInterface)
        klass.appList = klass.appHandler.getAppList(klass.user)
        for app in klass.boundApps:
            if not (app in klass.emailerApps):
                klass.app = app
                break
        klass.appNames = list()
        for anApp in klass.emailerApps:
            klass.appNames.append(anApp.name)


    @classmethod
    def createTestAppMaps(self):
        self.boundApps = set()
        self.emailerApps = list()
        for i in range(20): # @UnusedVariable
            name = self.createRandomUserId()
            newApp = Application.new(name, name, "https://{0}.com/".format(name))
            if (random.randint(1, 2) == 1):
                newApp.can_email = True
                newApp.save()
                self.emailerApps.append(newApp)
        self.allApps = set(Application.all())
        
        self.emailerMaps = list()
        for app in self.allApps:
            if (random.randint(1, 2) == 1):
                self.boundApps.add(app)
                m = AppMap.new(app, self.user)
                if app.can_email and (random.randint(1, 2) == 1):
                    m.can_email=True
                    self.emailerMaps.append(m)
                    m.save()

    def chooseAppWithOppositeEmailCapability(self, canEmail):
        for appName in self.appNames:
            theApp = Application.find(appName)
            theMap = AppMap.get(theApp,self.user)
            if theMap.can_email is not canEmail:
                return theApp
        
    def assertUserSetTheMap(self, app, theCase, theString):
        with app.test_client() as c:
            theApp = self.chooseAppWithOppositeEmailCapability(theCase)
            self.login(c, self.user)
            csrf = self.getCSRF(c)
            data = dict(
                csrf_token = csrf,
                appname=theApp.name,
                canemail=theString)
            resp = c.post("/v1/setappcanemail",data=data)
            self.assertEqual('200 OK', resp.status)
            self.assertEqual(theCase, AppMap.get(theApp,self.user).can_email)
    
