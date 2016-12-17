# -*- coding: UTF-8 -*-
from pdoauth.models.AppMap import AppMap
from pdoauth.models.Application import Application
from test.helpers.AppInfoUtil import AppInfoUtil
from pdoauth.ReportedError import ReportedError
from pdoauth import Messages

class AppInfoTest(AppInfoUtil):

    @classmethod
    def setUpClass(cls):
        AppInfoUtil.setUpClass()

    
    def test_appMap_can_email_is_false_by_default(self):
        appMap = AppMap.new(self.app,self.user)
        self.assertEqual(False,appMap.can_email)

    
    def test_appMap_can_email_is_false_even_if_the_app_can_email(self):
        appMap = AppMap.new(self.app,self.user)
        self.emailerApps.append(self.app)
        self.assertEqual(False,appMap.can_email)

    
    def test_the_list_of_applications_contain_all_applications_for_the_user(self):
        userMaps = AppMap.getForUser(self.user)
        appList = set()
        for appMap in userMaps:
            appList.add(appMap.app)
        self.assertEqual(self.boundApps,appList)
        
    
    def test_there_is_a_list_of_all_apps_denoting_the_user_data_associated_with_them(self):
        foundApps = set()
        for entry in self.appList:
            app = Application.find(entry['name'])
            foundApps.add(app)
        self.assertEqual(self.allApps, foundApps)

    
    def test_the_list_entries_contain_the_can_email_attribute_of_application(self):
        for app in self.appList:
            self.assertEqual(app['can_email'],Application.find(app['name']).can_email)

    
    def test_the_list_entries_contain_whether_the_user_enabled_emailing(self):
        missingCount= 0
        for entry in self.appList:
            app = Application.find(entry['name'])
            mapEntry=AppMap.find(app,self.user)
            if mapEntry:
                self.assertEqual(entry['email_enabled'], mapEntry.can_email)
            else:
                missingCount += 1
        self.assertTrue(missingCount < len(self.appList))
        self.assertTrue(missingCount > 0)

    
    def test_the_list_entries_contain_the_proxy_username(self):
        for entry in self.appList:
            app = Application.find(entry['name'])
            mapEntry=AppMap.find(app,self.user)
            if mapEntry:
                self.assertEqual(entry['username'], mapEntry.userid)

    
    def test_the_list_entries_contain_the_app_hostname(self):
        for entry in self.appList:
            app = Application.find(entry['name'])
            self.assertEqual(entry['hostname'], app.redirect_uri.split('/')[2])

    
    def test_the_user_can_set_the_can_email_attribute_of_the_app_map(self):
        boundApp = self.emailerApps[0]
        theMap = AppMap.get(boundApp, self.user)
        theMap.can_email = False
        self.appHandler.setCanEmail(boundApp.name, self.user, True)
        self.assertEqual(theMap.can_email, True)


    
    def test_the_user_can_unset_the_can_email_attribute_of_the_app_map(self):
        boundApp = self.emailerApps[0]
        theMap = AppMap.get(boundApp, self.user)
        theMap.can_email = True
        self.appHandler.setCanEmail(boundApp.name, self.user, False)
        self.assertEqual(theMap.can_email, False)

    
    def test_setting_can_email_for_unknown_app_raises_an_error(self):
        with self.assertRaises(ReportedError) as context:
            self.appHandler.setCanEmail('nonExisting App', self.user, False)
        self.assertEqual(Messages.unknownApplication, context.exception.descriptor)

