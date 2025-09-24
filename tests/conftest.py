"""
Pytest configuration and fixtures for cross-browser testing
"""
import pytest
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.browser_manager import BrowserManager


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome, firefox, edge, safari"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="https://www.saucedemo.com",
        help="Base URL for testing"
    )


@pytest.fixture(scope="function")
def browser(request):
    """Provide a browser instance for tests"""
    browser_name = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    # Initialize browser manager
    manager = BrowserManager(headless_override=headless)

    # Create browser instance
    driver = manager.get_browser(browser_name)

    # Make browser available to test
    yield driver

    # Cleanup - capture screenshot on failure
    if request.node.rep_call.failed:
        take_screenshot(driver, request.node.nodeid)

    driver.quit()


@pytest.fixture(scope="session")
def base_url(request):
    """Provide base URL for tests"""
    return request.config.getoption("--base-url")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test results available to fixtures"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def take_screenshot(driver, test_name):
    """Capture screenshot on test failure"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name_clean = test_name.replace("/", "_").replace("::", "_")

    screenshot_dir = Path(__file__).parent.parent / "reports" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = screenshot_dir / f"{test_name_clean}_{timestamp}.png"
    driver.save_screenshot(str(screenshot_path))
    print(f"\nScreenshot saved: {screenshot_path}")