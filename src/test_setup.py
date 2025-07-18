from browser_manager import BrowserManager


def test_browser_manager():
    """Test if browser manager is working"""
    manager = BrowserManager()
    print("Enabled browsers:", manager.get_enabled_browsers())

    # Try to create a Chrome browser
    try:
        driver = manager.get_browser('chrome')
        driver.get("https://www.google.com")
        print("✅ Chrome browser working!")
        print(f"Page title: {driver.title}")
        driver.quit()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_browser_manager()