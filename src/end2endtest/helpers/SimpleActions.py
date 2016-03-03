from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import end2endtest.helpers.TestEnvironment as TE

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

    def fillInField(self, fieldId, value):
        self.logAction('<fillinfield fieldid="{0}">'.format(fieldId))
        TE.driver.find_element_by_id(fieldId).clear()
        TE.driver.find_element_by_id(fieldId).send_keys(value)

    def click(self, fieldId):
        self.logAction('<click fieldid="{0}">'.format(fieldId))
        return TE.driver.find_element_by_id(fieldId).click()

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
        return self.wait_on_element_text(By.ID, "msg", "")

    def switchToTab(self,tab):
        TE.driver.find_element_by_id("{0}-menu".format(tab)).click()

    def closeMessage(self):
        self.waitForMessage()
        TE.driver.find_element_by_id("PopupWindow_CloseButton").click()

    def goToLoginPage(self):
        TE.driver.get(TE.loginUrl)
        self.waitLoginPage()

    def goToSSLLoginPage(self):
        TE.driver.get(TE.loginSSLUrl)
        self.waitLoginPage()
