"""
Login Page Object for SauceDemo site
"""
from selenium.webdriver.common.by import By
from tests.pages.base_pages import BasePage


class LoginPage(BasePage):
    """Page object for login functionality"""

    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver):
        super().__init__(driver)

    def login(self, username, password):
        """Perform login action"""
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self):
        """Get login error message"""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self):
        """Check if error message is displayed"""
        return self.is_displayed(self.ERROR_MESSAGE)