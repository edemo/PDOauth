import os
import logging
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pdoauth.models.Application import Application
from pdoauth.models import User
from pdoauth.CredentialManager import CredentialManager
from pdoauth.models.Assurance import Assurance
from end2endtest import config
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

print("setting up test environment")

def getDriver():
    if os.environ.get("WEBDRIVER", None) == "chrome":
        os.environ['PATH'] += ":/usr/lib/chromium-browser"
        options = Options()
        options.add_argument("--no-sandbox")
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = { 'browser':'ALL' }
        theDriver = webdriver.Chrome(chrome_options = options, desired_capabilities=d)
    else:
        d = DesiredCapabilities.FIREFOX
        d['marionette'] = True
        d['loggingPrefs'] = { 'browser':'ALL' }
        profile_directory = os.path.join(os.path.dirname(__file__),"..", "firefox-client-nossl-profile")
        profile = FirefoxProfile(profile_directory)
        profile.set_preference('webdriver.log.file', '/tmp/firefox_console')
        profile.set_preference("security.default_personal_cert", "Select Automatically")
        theDriver = webdriver.Firefox(firefox_profile=profile, capabilities=d)
    return theDriver

def getApplication():
    app = Application.find("testapp")
    if not app:
        app = Application.new("testapp", "S3cret", "https://app-none.github.com/")
    return app

def getAssurerUser():
    userName = "assurer"
    password = "Assur3rP4ssword"
    assurerEmail = "assurer@foo.bar"
    user = User.getByEmail(assurerEmail)
    if not user:
        user = CredentialManager.create_user_with_creds('password', userName, password, assurerEmail).user
        user.activate()
        Assurance.new(user, "assurer", user).save()
        Assurance.new(user, "assurer.test", user).save()
    user.password=password
    user.userName=userName
    return user
        
logging.basicConfig(level=logging.INFO)
baseUrl = config.Config.BASE_URL
backendPath = config.Config.BACKEND_PATH
backendUrl = baseUrl + backendPath
sslBaseUrl = config.Config.SSL_LOGIN_BASE_URL
loginPagePath = "/static/fiokom.html"
loginSSLUrl = sslBaseUrl + loginPagePath
loginUrl = baseUrl + loginPagePath
testUrl = baseUrl + "/static/test/test.html"
driver = getDriver()
app = getApplication()
assurerUser = getAssurerUser()
logfile = open("doc/activitylog.xml","w")


def newBrowser():
    global driver
    driver.quit()
    driver = getDriver()
