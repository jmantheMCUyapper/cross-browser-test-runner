"""Demo test suite to showcase framework capabilities"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class TestDemoSuite:
    """Comprehensive test suite for demo purposes"""

    def test_successful_google_search(self, browser):
        """✅ Test that demonstrates a passing test"""
        browser.get("https://www.google.com")
        assert "Google" in browser.title

        # Perform search
        search_box = browser.find_element(By.NAME, "q")
        search_box.send_keys("Selenium WebDriver")
        search_box.submit()

        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        assert "Selenium WebDriver" in browser.title

    def test_wikipedia_navigation(self, browser):
        """✅ Test navigation and page elements"""
        browser.get("https://www.wikipedia.org")

        # Test main page loads
        assert "Wikipedia" in browser.title

        # Find and click English link
        english_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "js-link-box-en"))
        )
        english_link.click()

        # Verify navigation
        assert "Wikipedia, the free encyclopedia" in browser.title

    def test_form_validation_failure(self, browser):
        """❌ Test that intentionally fails to show error handling"""
        browser.get("https://www.google.com")

        # This will fail to demonstrate failure handling
        assert "Bing" in browser.title, "Expected 'Bing' in title but found 'Google'"

    @pytest.mark.skip(reason="Demonstrating skip functionality")
    def test_skipped_test(self, browser):
        """⏭️ Test that is skipped to show skip handling"""
        browser.get("https://example.com")
        assert True

    def test_element_not_found_error(self, browser):
        """❌ Test that fails with element not found"""
        browser.get("https://www.google.com")

        # Try to find non-existent element
        with pytest.raises(TimeoutException):
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "non_existent_element"))
            )

    def test_github_profile_check(self, browser):
        """✅ Test GitHub profile page loads correctly"""
        browser.get("https://github.com")
        assert "GitHub" in browser.title

        # Check that main elements are present
        sign_in_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Sign in"))
        )
        assert sign_in_button is not None

    def test_response_time_check(self, browser):
        """✅ Test page load performance"""
        start_time = time.time()
        browser.get("https://www.example.com")
        load_time = time.time() - start_time

        assert load_time < 5, f"Page took {load_time:.2f} seconds to load"
        assert "Example Domain" in browser.title

    @pytest.mark.parametrize("search_term,expected", [
        ("Python", "Python"),
        ("Selenium", "Selenium"),
        ("Test Automation", "Test Automation")
    ])
    def test_parametrized_search(self, browser, search_term, expected):
        """✅ Parametrized test to show multiple test cases"""
        browser.get("https://www.google.com")

        search_box = browser.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.submit()

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        assert expected in browser.title