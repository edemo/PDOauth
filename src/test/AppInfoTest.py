# -*- coding: UTF-8 -*-
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.UserUtil import UserUtil
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.models.AppMap import AppMap
from pdoauth.models.Application import Application
from pdoauth.AppHandler import AppHandler
import random


class AppInfoTest(PDUnitTest, UserUtil, AuthProviderUtil):

    def setUp(self):
        self.user = self.createUserWithCredentials().user
        self.createTestAppMaps()
        self.app = self.boundApps.pop()
        self.boundApps.add(self.app)

    def createTestAppMaps(self):
        self.boundApps = set()
        for i in range(10): # @UnusedVariable
            name = self.createRandomUserId()
            Application.new(name, name, "https://{0}.com/".format(name))
        self.allApps = set(Application.all())
        
        for app in self.allApps:
            if (random.randint(1, 2) == 1):
                self.boundApps.add(app)
                m = AppMap.new(app, self.user)
                if (random.randint(1, 2) == 1):
                    m.can_email=True
                    m.save()


    @test
    def appMap_can_email_is_false_by_default(self):
        appMap = AppMap.new(self.app,self.user)
        self.assertEqual(False,appMap.can_email)

    @test
    def appMap_can_email_is_false_even_if_the_app_can_email(self):
        self.app.can_email = True
        appMap = AppMap.new(self.app,self.user)
        self.assertEqual(False,appMap.can_email)

    @test
    def there_is_a_list_of_applications_for_a_user(self):
        AppMap.getForUser(self.user)

    @test
    def the_list_of_applications_contain_all_applications_for_the_user(self):
        userMaps = AppMap.getForUser(self.user)
        appList = set()
        for appMap in userMaps:
            appList.add(appMap.app)
        self.assertEqual(self.boundApps,appList)
        
    @test
    def there_is_a_list_of_all_apps_denoting_the_user_data_associated_with_them(self):
        controller = AppHandler()
        appList = controller.getAppList(self.user)
        foundApps = set()
        print foundApps
        for entry in appList:
            app = Application.find(entry.name)
            foundApps.add(app)
        self.assertEqual(self.allApps, foundApps)

    @test
    def the_list_entries_contain_the_can_email_attribute_of_application(self):
        controller = AppHandler()
        appList = controller.getAppList(self.user)
        for app in appList:
            self.assertEqual(app.can_email,Application.find(app.name).can_email)
    @test
    def the_list_entries_contain_whether_the_user_enabled_emailing(self):
        controller = AppHandler()
        appList = controller.getAppList(self.user)
        missingCount= 0
        for entry in appList:
            app = Application.find(entry.name)
            mapEntry=AppMap.find(app,self.user)
            if mapEntry:
                self.assertEqual(entry.email_enabled, mapEntry.can_email)
            else:
                missingCount += 1
        self.assertTrue(missingCount < len(appList))
        self.assertTrue(missingCount > 0)

    @test
    def the_list_entries_contain_the_proxy_username(self):
        controller = AppHandler()
        appList = controller.getAppList(self.user)
        for entry in appList:
            app = Application.find(entry.name)
            mapEntry=AppMap.find(app,self.user)
            if mapEntry:
                self.assertEqual(entry.username, mapEntry.userid)

    @test
    def the_list_entries_contain_the_app_hostname(self):
        controller = AppHandler()
        appList = controller.getAppList(self.user)
        for entry in appList:
            app = Application.find(entry.name)
            self.assertEqual(entry.hostname, app.redirect_uri.split('/')[2])
