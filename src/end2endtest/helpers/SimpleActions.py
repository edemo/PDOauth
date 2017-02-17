from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import end2endtest.helpers.TestEnvironment as TE
import sys
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.webdriver import WebDriver as FIREFOXDRIVER
import time

class element_to_be_useable(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
        except:
            print(sys.exc_info())
            element = None
        if element:
            try:
                displayValue=element.value_of_css_property('display')
                displayok = displayValue in ('block', 'inline','inline-block')
                displayed = element.is_displayed()
                enabled = element.is_enabled()
                if displayed and enabled and displayok:
                    return element
            except StaleElementReferenceException:
                pass
        return False

class element_has_class(object):
    def __init__(self, locator, klass):
        self.locator = locator
        self.klass = klass

    def __call__(self, driver):
        try :
            element = driver.find_element(*self.locator)
        except:
            return False
        klass = element.get_attribute("class")
        if klass == self.klass:
            return element
        return False

class element_has_nonempty_text(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try :
            element = driver.find_element(*self.locator)
        except:
            return False
        value = element.get_attribute('value')
        if value != '':
            return element
        return False

class SimpleActions(object):
    currentProcess = list()

    def logAction(self,element):
        print(element)
        TE.logfile.write(element)
        TE.logfile.write("\n")

    def beginProcess(self, name):
        self.logAction('<process name="{0}">'.format(name))
        self.currentProcess.append(name)

    def endProcess(self, name):
        self.assertEqual(self.currentProcess.pop(), name)
        self.logAction('</process>')

    def waitUntilElementEnabled(self, fieldId):
        element = WebDriverWait(TE.driver, 10).until(element_to_be_useable((By.ID,fieldId)))
        return element

    def waitUntilElementHasText(self, fieldId):
        element = WebDriverWait(TE.driver, 10).until(element_has_nonempty_text((By.ID,fieldId)))
        return element

    def fillInField(self, fieldId, value):
        self.logAction('<fillinfield fieldid="{0}">'.format(fieldId))
        TE.driver.execute_script("""
            window.scrollTo(
                0,
                document.getElementById('{0}').getBoundingClientRect().top-
                 document.body.getBoundingClientRect().top-
                 100)""".format(fieldId))

        element = self.waitUntilElementEnabled(fieldId)
        element.clear()
        element.send_keys(value)

    def sendEnter(self, fieldId):
        self.logAction('<sendEnter fieldid="{0}">'.format(fieldId))
        element = TE.driver.find_element_by_id(fieldId)
        element.send_keys(Keys.ENTER)

    def selectOptionValue(self, fieldId, value):
        self.logAction('<selectOptionValue fieldid="{0}" value="{1}">'.format(fieldId, value))
        element = TE.driver.find_element_by_xpath("//select[@id='{0}']/option[@value='{1}']".format(fieldId, value))
        element.click()

    def clickCheckbox(self, elementId):
        self.logAction('<tickCheckbox fieldid="{0}">'.format(elementId))
        element = TE.driver.find_element_by_id(elementId)
        if type(TE.driver) == FIREFOXDRIVER:
            element.send_keys(Keys.SPACE)
        else:
            element.click()
        return element

    def tickCheckbox(self, elementId):
        element = self.clickCheckbox(elementId)
        self.assertTrue(element.is_selected())

    def untickCheckbox(self, elementId):
        element = self.clickCheckbox(elementId)
        self.assertFalse(element.is_selected())

    def click(self, fieldId):
        self.logAction('<click fieldid="{0}">'.format(fieldId))
        TE.driver.execute_script("""
            window.scrollTo(
                0,
                document.getElementById('{0}').getBoundingClientRect().top-
                 document.body.getBoundingClientRect().top-
                 100)""".format(fieldId))
        element = self.waitUntilElementEnabled(fieldId)
        TE.driver.execute_script("""
            window.scrollTo(
                0,
                document.getElementById('{0}').getBoundingClientRect().top-
                 document.body.getBoundingClientRect().top-
                 100)""".format(fieldId))
        return element.click()

    def observeField(self, fieldId):
        self.logAction('<observe fieldid="{0}">'.format(fieldId))
        body = TE.driver.find_element_by_id(fieldId).text
        return body

    def observeFieldValue(self, fieldId):
        self.logAction('<observe fieldid="{0}">'.format(fieldId))
        digest = TE.driver.find_element_by_id(fieldId).get_attribute('value')
        return digest

    def wait_on_element_text(self, by_type, element, text, timeout=20):
        self.logAction('<waitForText fieldid="{0}" text="{1}">'.format(element,text.encode('utf-8')))
        WebDriverWait(TE.driver, timeout).until(
            EC.text_to_be_present_in_element(
                (by_type, element), text)
        )

    def wait_on_element_class(self, by_type, element, klass):
        self.logAction('<waitForText fieldid="{0}" cclass="{1}">'.format(element,klass))
        WebDriverWait(TE.driver, 20).until(
            element_has_class(
                (by_type, element), klass)
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

    def waitForMessage2(self):
        return  WebDriverWait(TE.driver, 10).until(element_to_be_useable((By.ID,"myModal")))

    def haveAllTraces(self, labels):
        traces = self.getTraces()
        if traces is None:
            return False
        for label in labels:
            if label not in traces:
                return False
        return True

    def waitForTraces(self, traces):
        maxCount = 40
        count = 0
        while not self.haveAllTraces(traces):
            if count > maxCount:
                TE.driver.save_screenshot("shippable/pageTimeout.png")
                self.assertFalse("timeout waiting for javascript state")
            time.sleep(1)
            count += 1

    def waitLoginPage(self):
        self.waitForTraces(["initialized", "main end", "fbAsyncInit"])
        return self.waitUntilElementEnabled("nav-bar-aboutus")

    def waitContentProviderLoginPage(self):
        self.waitForTraces(["initialized", "fbAsyncInit", "loginpage"])
        return self.waitUntilElementEnabled("greatings")

    def switchToTab(self,tab):
        self.click("nav-bar-{0}_a".format(tab))
        self.waitUntilElementEnabled("{0}_section".format(tab))

    def switchToSection(self,tab):
        element = "{0}_section".format(tab)
        self.click(element)
        self.waitUntilElementEnabled("{0}_section".format(tab))

    def actuallyIHaveNoClueWhyWeHaveToWaitHere(self):
        time.sleep(1)

    def closeMessage(self, closeWait=True):
        self.waitForMessage2()
        self.waitForTraces(['MSGbox ready'])
        TE.driver.find_element_by_id("PopupWindow_CloseButton2").click()
        if closeWait:
            self.waitForTraces(['popup closed'])
        self.actuallyIHaveNoClueWhyWeHaveToWaitHere()

    def goToLoginPage(self):
        TE.driver.get(TE.loginUrl)
        self.waitLoginPage()

    def goToRegisterPage(self):
        TE.driver.get("{0}?section=register".format(TE.loginUrl))
        self.waitForTraces(["userIsNotLoggedIn"])
		self.waitUntilElementEnabled("registration-form_email_input")

    def goToTestPage(self):
        TE.driver.get(TE.testUrl)
        self.waitUntilElementEnabled("e2e")

    def goToSSLLoginPage(self):
        TE.driver.get(TE.loginSSLUrl)
        self.waitLoginPage()

    def getTraces(self):
        traces = TE.driver.execute_script("return window.traces")
        print(traces)
        return traces
