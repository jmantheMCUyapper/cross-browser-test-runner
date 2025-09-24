"""
Browser Manager - Handles browser driver initialization and configuration
"""
import logging
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import yaml
import os
import platform

logger = logging.getLogger(__name__)


class BrowserNotFoundError(Exception):
    """Raised when a browser is not installed on the system"""
    pass


class BrowserManager:
    """Manages browser driver creation and configuration"""

    def __init__(self, config_path: str = None, headless_override: Optional[bool] = None):
        """Initialize browser manager with configuration"""
        if config_path is None:
            # Find config file relative to project root
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "browsers.yaml"

        self.config = self._load_config(str(config_path))
        if headless_override is not None:
            for browser_config in self.config['browsers'].values():
                browser_config['headless'] = headless_override
        self.supported_browsers = {
            'chrome': self._create_chrome,
            'firefox': self._create_firefox,
            'edge': self._create_edge,
            'safari': self._create_safari
        }
        self.available_browsers = self._detect_available_browsers()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load browser configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found. Using defaults.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'browsers': {
                'chrome': {'enabled': True, 'headless': False, 'options': []},
                'firefox': {'enabled': True, 'headless': False, 'options': []},
                'edge': {'enabled': True, 'headless': False, 'options': []},
                'safari': {'enabled': False, 'headless': False, 'options': []}
            }
        }

    def _detect_available_browsers(self) -> Dict[str, bool]:
        """Detect which browsers are installed on the system"""
        available = {}

        # Check Chrome
        chrome_paths = {
            'Windows': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ],
            'Darwin': ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            'Linux': ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
        }

        # Check Firefox
        firefox_paths = {
            'Windows': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            'Darwin': ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            'Linux': ["/usr/bin/firefox"]
        }

        # Check Edge
        edge_paths = {
            'Windows': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ],
            'Darwin': ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
            'Linux': ["/usr/bin/microsoft-edge"]
        }

        system = platform.system()

        # Check each browser
        available['chrome'] = any(os.path.exists(path) for path in chrome_paths.get(system, []))
        available['firefox'] = any(os.path.exists(path) for path in firefox_paths.get(system, []))
        available['edge'] = any(os.path.exists(path) for path in edge_paths.get(system, []))
        available['safari'] = system == 'Darwin'  # Safari only on macOS

        logger.info(f"Detected browsers: {available}")
        return available

    def get_browser(self, browser_name: str) -> webdriver.Remote:
        """Create and return a configured browser instance"""
        browser_name = browser_name.lower()

        if browser_name not in self.supported_browsers:
            raise ValueError(f"Browser '{browser_name}' is not supported. "
                             f"Supported browsers: {list(self.supported_browsers.keys())}")

        browser_config = self.config['browsers'].get(browser_name, {})
        if not browser_config.get('enabled', False):
            raise ValueError(f"Browser '{browser_name}' is disabled in configuration")

        # Check if browser is installed
        if not self.available_browsers.get(browser_name, False):
            raise BrowserNotFoundError(
                f"{browser_name.title()} browser is not installed on this system. "
                f"Please install {browser_name.title()} or disable it in the configuration."
            )

        logger.info(f"Creating {browser_name} browser instance...")

        try:
            return self.supported_browsers[browser_name](browser_config)
        except SessionNotCreatedException as e:
            if "binary location" in str(e) or "Unable to find" in str(e):
                raise BrowserNotFoundError(
                    f"{browser_name.title()} browser not found at expected location. "
                    f"Please ensure {browser_name.title()} is properly installed."
                )
            else:
                raise
        except WebDriverException as e:
            logger.error(f"WebDriver error for {browser_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating {browser_name} browser: {e}")
            raise

    def _create_chrome(self, config: Dict[str, Any]) -> webdriver.Chrome:
        """Create Chrome browser instance"""
        options = webdriver.ChromeOptions()

        # Add custom options from config
        for option in config.get('options', []):
            options.add_argument(option)

        # Set headless if configured
        if config.get('headless', False):
            options.add_argument('--headless=new')

        # Windows-specific options
        if platform.system() == 'Windows':
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')

        # Additional Chrome-specific options
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        self._configure_timeouts(driver)
        return driver

    def _create_firefox(self, config: Dict[str, Any]) -> webdriver.Firefox:
        """Create Firefox browser instance"""
        options = webdriver.FirefoxOptions()

        # Add custom options from config
        for option in config.get('options', []):
            options.add_argument(option)

        # Set headless if configured
        if config.get('headless', False):
            options.add_argument('--headless')

        # Set Firefox binary location if needed
        if platform.system() == 'Windows':
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            for path in firefox_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    break

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        self._configure_timeouts(driver)
        return driver

    def _create_edge(self, config: Dict[str, Any]) -> webdriver.Edge:
        """Create Edge browser instance"""
        options = webdriver.EdgeOptions()

        # Add custom options from config
        for option in config.get('options', []):
            options.add_argument(option)

        # Set headless if configured
        if config.get('headless', False):
            options.add_argument('--headless')

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        self._configure_timeouts(driver)
        return driver

    def _create_safari(self, config: Dict[str, Any]) -> webdriver.Safari:
        """Create Safari browser instance (macOS only)"""
        if platform.system() != 'Darwin':
            raise BrowserNotFoundError("Safari is only available on macOS")

        # Safari doesn't support many options like other browsers
        driver = webdriver.Safari()
        self._configure_timeouts(driver)
        return driver

    def _configure_timeouts(self, driver: webdriver.Remote) -> None:
        """Configure driver timeouts from settings"""
        settings = self.config.get('test_settings', {})
        implicit_wait = settings.get('implicit_wait', 10)
        driver.implicitly_wait(implicit_wait)

    def get_enabled_browsers(self) -> list:
        """Return list of enabled browser names"""
        enabled = []
        for browser, config in self.config['browsers'].items():
            if config.get('enabled', False):
                enabled.append(browser)
        return enabled

    def get_available_enabled_browsers(self) -> list:
        """Return list of browsers that are both enabled and installed"""
        enabled = self.get_enabled_browsers()
        available = []

        for browser in enabled:
            if self.available_browsers.get(browser, False):
                available.append(browser)
            else:
                logger.warning(f"{browser.title()} is enabled but not installed")

        return available