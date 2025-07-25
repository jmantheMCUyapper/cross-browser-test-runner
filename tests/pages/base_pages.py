"""
Base Page class with common functionality
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BasePage:
    """Base class for all page objects"""

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def go_to(self, url):
        """Navigate to a URL"""
        self.driver.get(url)

    def find_element(self, locator):
        """Find element with explicit wait"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        """Find multiple elements"""
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        """Click an element"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator, text):
        """Type text into an input field"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        """Get text from an element"""
        element = self.find_element(locator)
        return element.text

    def is_displayed(self, locator):
        """Check if element is displayed"""
        try:
            element = self.find_element(locator)
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_url_contains(self, partial_url):
        """Wait for URL to contain specific text"""
        return self.wait.until(EC.url_contains(partial_url))

    def get_title(self):
        """Get page title"""
        return self.driver.title

    def take_screenshot(self, filename):
        """Take a screenshot"""
        return self.driver.save_screenshot(filename)

    def scroll_to_element(self, locator):
        """Scroll to make element visible"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def hover_over_element(self, locator):
        """Hover over an element"""
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()