from urllib import urlencode
from selenium.webdriver.common.by import By
from pdoauth.models.User import User
from test.helpers.RandomUtil import RandomUtil
import end2endtest.helpers.TestEnvironment as TE
import os
from selenium.common.exceptions import TimeoutException
import time
from end2endtest import config
from FacebookUtil import FacebookUtil
from Assertions import Assertions
from SimpleActions import SimpleActions
from ComplexProcedures import ComplexProcedures

class BrowsingUtil(RandomUtil, FacebookUtil, Assertions, SimpleActions, ComplexProcedures):

    def callOauthUri(self):
        oauthUri = "{0}/v1/oauth2/auth?{1}".format(TE.backendUrl, urlencode({
                    "response_type":"code", 
                    "client_id":TE.app.appid, 
                    "redirect_uri":TE.app.redirect_uri}))
        TE.driver.get(oauthUri)
        self.waitLoginPage()
        uri = "{0}/static/login.html?{1}".format(TE.baseUrl, urlencode({"next":oauthUri}))
        self.assertEqual(uri, TE.driver.current_url)

    def waitForWindow(self):
        timeCount = 1;
        while (len(TE.driver.window_handles) == 1 ):
            timeCount += 1
            time.sleep(1)
            if ( timeCount > 5 ): 
                raise TimeoutException()
        
    def swithToPopUp(self):
        for handle in TE.driver.window_handles:
            if handle != self.master:
                TE.driver.switch_to.window(handle)

    def saveQunitXml(self):
        self.wait_on_element_text(By.ID, "qunit-testresult", "failed")
        xml = TE.driver.find_element_by_id("qunit-xml").get_attribute("innerHTML")
        mypath = os.path.abspath(__file__)
        up = os.path.dirname
        xmlpath = os.path.join(up(up(up(up(mypath)))), "doc/screenshots/unittests.xml")
        xmlFile = open(xmlpath, "w")
        xmlFile.write(xml)
        xmlFile.close()

    def getAssurerUser(self):
        return TE.assurerUser

    def tearDown(self):
        self.logOut()
        fbuser = User.getByEmail(config.facebookUser1.email)
        if fbuser:
            fbuser.rm()

