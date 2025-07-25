"""
Cross-browser compatibility tests
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestCrossBrowserCompatibility:
    """Tests specifically designed to check cross-browser compatibility"""

    def test_basic_navigation(self, browser):
        """Test basic navigation works across browsers"""
        # Navigate to example.com
        browser.get("https://example.com")

        # Verify page loaded
        assert "Example Domain" in browser.title

        # Find and verify main heading
        heading = browser.find_element(By.TAG_NAME, "h1")
        assert heading.text == "Example Domain"

    def test_window_resize(self, browser):
        """Test window resizing across browsers"""
        browser.get("https://example.com")

        # Test different window sizes
        sizes = [(1920, 1080), (1366, 768), (375, 667)]

        for width, height in sizes:
            browser.set_window_size(width, height)
            current_size = browser.get_window_size()

            # Allow small differences due to browser chrome
            assert abs(current_size['width'] - width) < 50
            assert abs(current_size['height'] - height) < 150

    def test_javascript_execution(self, browser):
        """Test JavaScript execution across browsers"""
        browser.get("https://example.com")

        # Execute JavaScript
        result = browser.execute_script("return navigator.userAgent")
        assert result is not None

        # Modify page with JavaScript
        browser.execute_script("""
            document.querySelector('h1').style.color = 'red';
            document.querySelector('h1').setAttribute('data-test', 'modified');
        """)

        # Verify modification worked
        heading = browser.find_element(By.TAG_NAME, "h1")
        assert heading.get_attribute("data-test") == "modified"

    def test_form_inputs(self, browser):
        """Test form input handling across browsers"""
        browser.get("https://the-internet.herokuapp.com/login")

        # Find form elements
        username = browser.find_element(By.ID, "username")
        password = browser.find_element(By.ID, "password")
        submit_btn = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Test input
        username.send_keys("tomsmith")
        password.send_keys("SuperSecretPassword!")

        # Verify values were entered
        assert username.get_attribute("value") == "tomsmith"
        assert password.get_attribute("value") == "SuperSecretPassword!"

        # Submit form
        submit_btn.click()

        # Wait for success message
        wait = WebDriverWait(browser, 10)
        flash_msg = wait.until(
            EC.presence_of_element_located((By.ID, "flash"))
        )
        assert "You logged into a secure area!" in flash_msg.text

    def test_cookies(self, browser):
        """Test cookie handling across browsers"""
        browser.get("https://example.com")

        # Add a cookie
        browser.add_cookie({
            "name": "test_cookie",
            "value": "test_value",
            "path": "/"
        })

        # Retrieve cookie
        cookie = browser.get_cookie("test_cookie")
        assert cookie is not None
        assert cookie["value"] == "test_value"

        # Delete cookie
        browser.delete_cookie("test_cookie")
        assert browser.get_cookie("test_cookie") is None