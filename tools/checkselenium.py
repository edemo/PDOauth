from selenium import webdriver
import pdb

driver = webdriver.Chrome()
driver.get("https://bugs.chromium.org/p/chromedriver/issues/list")
inputElement = driver.find_element_by_id("searchq")
inputElement.send_keys("more words")
result=inputElement.get_attribute('value')
if result != "more words":
    print "got %s instead of 'more words'"%(result)
    pdb.set_trace()
else:
    print "This combination works"

