# -*- coding: UTF-8 -*-
from test.helpers.PDUnitTest import test
from pdoauth.models.AppMap import AppMap
from test.helpers.AppInfoUtil import AppInfoUtil

class AppMapTest(AppInfoUtil):

    
    def test_proxy_id_is_not_created_deterministically(self):
        cred = self.createLoggedInUser()
        app = self.app
        mapentry = AppMap(app, cred.user)
        mapentry.save()
        oldid = mapentry.userid
        mapentry.rm();
        mapentry = AppMap(app, cred.user)
        self.assertNotEqual(oldid, mapentry.userid)
