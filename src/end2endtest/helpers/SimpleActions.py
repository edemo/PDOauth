from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import end2endtest.helpers.TestEnvironment as TE
import sys
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import time
import unittest

class element_to_be_useable(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
        except:
            print sys.exc_info()
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
        element = self.waitUntilElementEnabled(fieldId)
        element.clear()
        element.send_keys(value)

    def selectOptionValue(self, fieldId, value):
        self.logAction('<selectOptionValue fieldid="{0}" value="{1}">'.format(fieldId, value))
        element = TE.driver.find_element_by_xpath("//select[@id='{0}']/option[@value='{1}']".format(fieldId, value))
        element.click()

    def tickCheckbox(self, elementId):
        self.logAction('<tickCheckbox fieldid="{0}">'.format(elementId))
        element = TE.driver.find_element_by_id(elementId)
        element.send_keys(Keys.SPACE)
        print elementId
        selected = False
        for t in range(10):
            time.sleep(1)
            print "slept"
            if element.is_selected():
                selected = True
                break
        self.assertTrue(selected)
            


    def click(self, fieldId):
        self.logAction('<click fieldid="{0}">'.format(fieldId))
        element = self.waitUntilElementEnabled(fieldId)
        print element, element.tag_name.encode("utf-8"), element.id.encode("utf-8"), element.text.encode("utf-8")
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

    def waitLoginPage(self):
        return self.waitUntilElementEnabled("nav-bar-aboutus")

    def waitContentProviderLoginPage(self):
        return self.waitUntilElementEnabled("greatings")

    def switchToTab(self,tab):
        self.click("nav-bar-{0}".format(tab))
        self.waitUntilElementEnabled("{0}_section".format(tab))

    def switchToSection(self,tab):
        element = "{0}_section".format(tab)
        self.click(element)
        self.waitUntilElementEnabled("{0}_section".format(tab))

    def closeMessage(self):
        self.waitForMessage2()
        TE.driver.find_element_by_id("PopupWindow_CloseButton2").click()

    def goToLoginPage(self):
        TE.driver.get(TE.loginUrl)
        self.waitLoginPage()

    def goToTestPage(self):
        TE.driver.get(TE.testUrl)
        self.waitUntilElementEnabled("e2e")

    def goToSSLLoginPage(self):
        TE.driver.get(TE.loginSSLUrl)
        self.waitLoginPage()
