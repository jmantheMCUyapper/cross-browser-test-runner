"""
Login functionality tests
"""
import pytest
from tests.pages.login_page import LoginPage
from tests.pages.inventory_page import InventoryPage


@pytest.mark.smoke
@pytest.mark.ui
class TestLogin:
    """Test login functionality across browsers"""

    @pytest.fixture(autouse=True)
    def setup(self, browser, base_url):
        """Setup test dependencies"""
        self.browser = browser
        self.base_url = base_url
        self.login_page = LoginPage(browser)
        self.inventory_page = InventoryPage(browser)

        # Navigate to login page
        browser.get(base_url)

    def test_successful_login(self):
        """Test successful login with valid credentials"""
        # Perform login
        self.login_page.login("standard_user", "secret_sauce")

        # Verify successful login
        assert self.inventory_page.is_on_inventory_page(), "Login failed - not on inventory page"
        assert "inventory.html" in self.browser.current_url

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Attempt login with wrong password
        self.login_page.login("standard_user", "wrong_password")

        # Verify error message
        assert self.login_page.is_error_displayed(), "Error message not displayed"
        error_text = self.login_page.get_error_message()
        assert "Username and password do not match" in error_text

    def test_login_with_locked_user(self):
        """Test login with locked out user"""
        # Attempt login with locked user
        self.login_page.login("locked_out_user", "secret_sauce")

        # Verify error message
        assert self.login_page.is_error_displayed()
        error_text = self.login_page.get_error_message()
        assert "Sorry, this user has been locked out" in error_text

    @pytest.mark.parametrize("username,password", [
        ("", "secret_sauce"),
        ("standard_user", ""),
        ("", ""),
    ])
    def test_login_with_empty_fields(self, username, password):
        """Test login with empty username or password"""
        # Attempt login
        self.login_page.login(username, password)

        # Verify error message
        assert self.login_page.is_error_displayed()
        error_text = self.login_page.get_error_message()
        assert "required" in error_text.lower()