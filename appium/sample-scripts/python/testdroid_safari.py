##
## For help on setting up your machine and configuring this TestScript go to
## http://docs.testdroid.com/appium/
##

import os
import time
import unittest
from time import sleep
from appium import webdriver
from device_finder import DeviceFinder
from selenium.common.exceptions import NoSuchElementException

def log(msg):
    print (time.strftime("%H:%M:%S") + ": " + msg)

class TestdroidSafari(unittest.TestCase):

    """
    Take screenshot and store files to defined location, with numbering prefix

    :Args:
    - name - files are stored as #_name
    """
    def screenshot(self, name):
        screenshot_name = str(self.screenshot_count) + "_" + name + ".png"
        log ("Taking screenshot: " + screenshot_name)
        self.driver.save_screenshot(self.screenshot_dir + "/" + screenshot_name)
        self.screenshot_count += 1

    """
    Search for specified xpath for defined period

    :Args:

    - xpath - the xpath to search for

    - timeout - duration in seconds to search for given xpath

    - step - how often to search run the search

    :Usage:
    self.wait_until_xpath_matches("//div[@id='example']", 15, 2)"
    """
    def wait_until_xpath_matches(self, xpath, timeout=10, step=1):
        end_time = time.time() + timeout
        found = False
        while (time.time() < end_time and not found):
            log("  Looking for xpath {}".format(xpath))
            try:
                elem = self.driver.find_element_by_xpath(xpath)
                found = True
            except NoSuchElementException:
                found = False
            time.sleep(step)
        self.assertTrue(found, "Xpath '{}' not found in {}s".format(xpath, timeout))
        return elem

    def setUp(self):
        ##
        ## IMPORTANT: Set the following parameters.
        ##
        testdroid_url = os.environ.get('TESTDROID_URL') or "https://cloud.testdroid.com"
        appium_url = os.environ.get('TESTDROID_APPIUM_URL') or 'http://appium.testdroid.com/wd/hub'
        testdroid_apiKey = os.environ.get('TESTDROID_APIKEY') or ""
        testdroid_project_name = os.environ.get('TESTDROID_PROJECT') or "Safari sample project"
        testdroid_testrun_name = os.environ.get('TESTDROID_TESTRUN') or "My testrun"
        new_command_timeout = os.environ.get('TESTDROID_CMD_TIMEOUT') or '60'
        testdroid_test_timeout = os.environ.get('TESTDROID_TEST_TIMEOUT') or '600'

        self.screenshot_dir = os.environ.get('TESTDROID_SCREENSHOTS') or os.getcwd() + "/screenshots"
        log ("Will save screenshots at: " + self.screenshot_dir)
        self.screenshot_count = 1

        # Options to select device
        # 1) Set environment variable TESTDROID_DEVICE
        # 2) Set device name to this python script
        # 3) Do not set #1 and #2 and let DeviceFinder to find free device for you
        testdroid_device = os.environ.get('TESTDROID_DEVICE') or ""

        deviceFinder = DeviceFinder(url=testdroid_url)
        if testdroid_device == "":
            # Loop will not exit until free device is found
            while testdroid_device == "":
                testdroid_device = deviceFinder.available_free_ios_device()

        print "Starting Appium test using device '%s'" % testdroid_device

        desired_capabilities_cloud = {}
        desired_capabilities_cloud['testdroid_apiKey'] = testdroid_apiKey
        desired_capabilities_cloud['testdroid_target'] = 'safari'
        desired_capabilities_cloud['testdroid_project'] = testdroid_project_name
        desired_capabilities_cloud['testdroid_testrun'] = testdroid_testrun_name
        desired_capabilities_cloud['testdroid_device'] = testdroid_device
        desired_capabilities_cloud['platformName'] = 'iOS'
        desired_capabilities_cloud['deviceName'] = 'iOS Device'
        desired_capabilities_cloud['browserName'] = 'Safari'
        desired_capabilities_cloud['newCommandTimeout'] = new_command_timeout
        desired_capabilities_cloud['testdroid_testTimeout'] = testdroid_test_timeout

        # Set up webdriver
        log ("WebDriver request initiated. Waiting for response, this typically takes 2-3 mins")
        self.driver = webdriver.Remote(appium_url, desired_capabilities_cloud)

        log ("Loading page http://docs.testdroid.com")
        self.driver.get("http://docs.testdroid.com")

    def tearDown(self):
        log ("Quitting")
        self.driver.quit()

    def testSample(self):
        self.screenshot("home_screen")

        log ("  Switching to landscape")
        self.driver.orientation = "LANDSCAPE"
        self.screenshot("results_landscape")
        log ("  Switching to portrait")
        self.driver.orientation = "PORTRAIT"
        self.screenshot("results_portrait")

        log ("Finding 'search button'")
        elem = self.wait_until_xpath_matches('//input[@id="search"]')

        log ("Typing to search field")
        elem.send_keys("appium")
        self.screenshot("search_text")

        log ("Click search")
        elem = self.driver.find_element_by_xpath('//input[@class="search-button"]')
        elem.click()

        log ("Look for result text heading")
        # workaround, since h1 doesn't include all the text in one text() element
        end_time = time.time() + 30
        while time.time() < end_time:
            # wait up to 10s to get search results
            elem = self.wait_until_xpath_matches('//h1[contains(text(), "Search results")]', 10)
            if "appium" in elem.text:
                end_time = time.time()
        
        self.screenshot("search_title_present")
        log ("Verify correct heading text")
        log ("h1 text: " + str(elem.text))
        self.assertTrue("Search results for \"appium\"" in str(elem.text))

def initialize():
    return TestdroidSafari


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestdroidSafari)
    unittest.TextTestRunner(verbosity=2).run(suite)
