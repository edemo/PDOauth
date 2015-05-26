from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os
import shutil

class BrowserSetup:

    def getDriver(self, profile=None, autoselect=None):
        self.setProfileDirectory()
        if os.environ.get("WEBDRIVER", None) == "chrome":
            os.environ['PATH'] += ":/usr/lib/chromium-browser"
            self.profile = webdriver.ChromeOptions();
            if profile is not None:
                self.profile.add_argument("user-data-dir={0}".format(self.profile_directory));
            theDriver = webdriver.Chrome(chrome_options=self.profile)
        else:
            if profile is not None:
                self.profile = FirefoxProfile(self.profile_directory)
                if autoselect is not None:
                    self.profile.set_preference("security.default_personal_cert", "Select Automatically")
            else:
                self.profile = FirefoxProfile()
            theDriver = webdriver.Firefox(firefox_profile=self.profile)
        return theDriver
    
    def setProfileDirectory(self):
        if os.environ.get("WEBDRIVER", None) == "chrome":
            profile_directory = os.path.join(os.path.dirname(__file__), "chromium-client-ssl-profile")
            self.profile_directory=os.tmpnam()
            shutil.copytree(profile_directory, self.profile_directory)
        else:
            self.profile_directory = os.path.join(os.path.dirname(__file__), "firefox-client-ssl-profile")

    def setupDriver(self):
        self.driver = self.getDriver()
        self.driver.implicitly_wait(5)
        self.driver.set_page_load_timeout(10)
        return self.driver

    def setupDefCertDriver(self):
        self.defcertDriver = self.getDriver(profile=True, autoselect=True)
        self.defcertDriver.implicitly_wait(10)

    def setupCertAskingDriver(self):
        driver = self.getDriver(profile=True)
        return driver


