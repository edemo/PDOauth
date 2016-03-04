from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import end2endtest.helpers.TestEnvironment as TE
import sys

class element_to_be_useable(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        print self.locator
        try:
            element = driver.find_element(*self.locator)
        except:
            print sys.exc_info()
            element = None
        #print "e=",element
        if element:
            displayValue=element.value_of_css_property('display')
            displayok = displayValue in ('block', 'inline','inline-block')
            displayed = element.is_displayed()
            enabled = element.is_enabled()
            #print displayValue, displayed, enabled
            if displayed and enabled and displayok:
                return element
        return False

class SimpleActions(object):
    
    def logAction(self,element):
        TE.logfile.write(element)
        TE.logfile.write("\n")
    
    def beginProcess(self, name):
        self.logAction('<process name="{0}">'.format(name))
        self.currentProcess = name

    def endProcess(self, name):
        self.assertEqual(self.currentProcess, name)
        self.logAction('</process>')

    def waitUntilElementEnabled(self, fieldId):
        element = WebDriverWait(TE.driver, 10).until(element_to_be_useable((By.ID,fieldId)))
        return element

    def fillInField(self, fieldId, value):
        self.logAction('<fillinfield fieldid="{0}">'.format(fieldId))
        element = self.waitUntilElementEnabled(fieldId)
        element.clear()
        element.send_keys(value)

    def click(self, fieldId):
        self.logAction('<click fieldid="{0}">'.format(fieldId))
        element = self.waitUntilElementEnabled(fieldId)
        return element.click()

    def observeField(self, fieldId):
        self.logAction('<observe fieldid="{0}">'.format(fieldId))
        body = TE.driver.find_element_by_id(fieldId).text
        return body

    def observeFieldValue(self, fieldId):
        self.logAction('<observe fieldid="{0}">'.format(fieldId))
        digest = TE.driver.find_element_by_id(fieldId).get_attribute('value')
        return digest

    def wait_on_element_text(self, by_type, element, text):
        WebDriverWait(TE.driver, 20).until(
            EC.text_to_be_present_in_element(
                (by_type, element), text)
        )

    def wait_on_element(self, by_type, element):
        WebDriverWait(TE.driver, 20).until(
            EC.presence_of_element_located(
                (by_type, element))
        )

    def waitFortestAppRedirectUri(self):
        return self.wait_on_element_text(By.TAG_NAME, "h1", "404")

    def waitForMessage(self):
        return self.wait_on_element_text(By.ID, "PopupWindow_CloseButton", "Close")

    def waitLoginPage(self):
        return self.waitUntilElementEnabled("qunit-header")

    def switchToTab(self,tab):
        self.click("{0}-menu".format(tab))
        self.waitUntilElementEnabled("tab-content-{0}".format(tab))

    def closeMessage(self):
        self.waitForMessage()
        TE.driver.find_element_by_id("PopupWindow_CloseButton").click()

    def goToLoginPage(self):
        TE.driver.get(TE.loginUrl)
        self.waitLoginPage()

    def goToSSLLoginPage(self):
        TE.driver.get(TE.loginSSLUrl)
        self.waitLoginPage()
