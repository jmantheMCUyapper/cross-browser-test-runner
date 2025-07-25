# 🚀 Cross-Browser Test Automation Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0%2B-green)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/jmantheMCUyapper/cross-browser-test-framework/graphs/commit-activity)

A professional, scalable test automation framework for running Selenium tests across multiple browsers with beautiful HTML reports and comprehensive test analytics.

## ✨ Features

- 🌐 **Multi-Browser Support**: Chrome, Firefox, Edge, and Safari
- 📊 **Beautiful HTML Reports**: Interactive charts and detailed test results
- 🚦 **Automatic Browser Detection**: Gracefully handles missing browsers
- 🎯 **Flexible Test Execution**: Run specific tests on specific browsers
- 📈 **Test Analytics**: Duration tracking, pass/fail trends, error distribution
- 🔧 **Easy Configuration**: JSON-based configuration files
- 🎨 **Professional CLI**: Rich command-line interface with progress indicators
- 🐛 **Comprehensive Error Handling**: Detailed error messages and stack traces

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome, Firefox, or Edge browser installed

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cross-browser-test-runner.git
cd cross-browser-test-runner
```

2. Install Dependencies:
```bash
pip install -r requirements.txt
```

3. Download WebDrivers (optional)
```bash
The framework will automatically download drivers when needed
Or manually download from:
ChromeDriver: https://chromedriver.chromium.org/
GeckoDriver: https://github.com/mozilla/geckodriver/releases
EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
```

## Running Tests
Using the CLI (Recommended)
```bash
# Show available commands
python cli.py --help

# List available browsers
python cli.py browsers

# Run all tests on all configured browsers
python cli.py run --open-report

# Run specific tests on specific browsers
python cli.py run --browsers chrome firefox --tests tests/test_login.py

# Run tests in headless mode
python cli.py run --headless

# View the latest report
python cli.py report
```



Using Python directly
```python
from src.test_runner import TestRunner

# Run tests with default configuration
runner = TestRunner()
results = runner.run_tests()
```

### Running Tests with Markers

```bash
# Run only smoke tests
python cli.py run -- -m smoke

# Run UI tests but not slow ones
python cli.py run -- -m "ui and not slow"

# Run regression tests on specific browser
python cli.py run --browsers chrome -- -m regression

# Run cross-browser tests
python cli.py run -- -m cross_browser
```

## 📁 Project Structure
```text
cross-browser-test-runner/
├── src/
│   ├── __init__.py
│   ├── browser_manager.py      # Browser detection and WebDriver management
│   ├── test_runner.py          # Core test execution engine
│   ├── report_generator.py     # HTML report generation with charts
│   └── retry_helper.py         # Connection retry utilities (KEEP!)
├── tests/
│   ├── conftest.py             # Pytest fixtures and hooks (KEEP HERE)
│   ├── demo_suite.py           # Demo tests showcasing features
│   ├── pages/                  # Page Object Model classes
│   │   └── [page classes]
│   └── sample_tests/
│       └── test_login.py       # Example test files
├── config/
│   ├── browsers.yaml           # Browser configuration (KEEP!)
│   ├── test_config.json        # Main test configuration
│   └── demo_config.json        # Demo test configuration
├── cli.py                      # Command-line interface
├── pytest.ini                  # Pytest configuration (KEEP!)
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 🔧 Configuration Files

### browsers.yaml
Defines browser detection patterns and driver paths.

### test_config.json
Main configuration for test execution:
- Browser selection
- Test file paths
- Execution settings
- Report preferences
```json
{
  "browsers": ["chrome", "firefox", "edge"],  // Which browsers to test on
  "test_files": ["tests/"],                   // Where to find test files
  "parallel_execution": false,                // Run tests at same time (faster)
  "headless": false,                          // Run without showing browser window
  "timeout": 30,                              // How long to wait for elements (seconds)
  "window_size": {
    "width": 1920,                            // Browser window width
    "height": 1080                            // Browser window height
  },
  "implicit_wait": 10,                        // Default wait time for elements
  "report_settings": {
    "generate_html": true,                    // Create HTML reports
    "include_screenshots": true               // Take screenshots on failures
  }
}
```

### pytest.ini
Pytest-specific configuration:
- Test discovery patterns
- Custom markers (smoke, regression, cross_browser)
- Output formatting options


## 📝 Writing Tests

Tests are written using pytest and Selenium WebDriver. The framework provides a `browser` fixture that automatically manages WebDriver instances.

### Basic Test Structure

```python
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestExample:
    def test_google_search(self, browser):
        """Test Google search functionality"""
        # Navigate to website
        browser.get("https://www.google.com")
        
        # Find and interact with elements
        search_box = browser.find_element(By.NAME, "q")
        search_box.send_keys("Selenium WebDriver")
        search_box.submit()
        
        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Assert results
        assert "Selenium WebDriver" in browser.title
```

## 📊 Test Reports

The framework generates beautiful, interactive HTML reports after each test run.

### Report Features

- **📈 Summary Dashboard**: Quick overview of test results
- **📊 Interactive Charts**: 
  - Pass/Fail distribution pie chart
  - Browser performance comparison
  - Test execution timeline
  - Error type distribution
- **📋 Detailed Results**: Complete test logs with error traces
- **🖼️ Screenshots**: Automatic capture on test failures
- **⏱️ Performance Metrics**: Test duration and trends

### Accessing Reports

Reports are automatically saved in the `results/` directory:
```text
results/
└── report_20240115_143052/
├── index.html # Main report file
├── results.json # Raw test data
└── screenshots/ # Failure screenshots
```

### Open the latest report:
```bash
python cli.py report
```

### Viewing Reports
Option 1: Automatic Opening
```bash
python cli.py run --open-report
```

Option 2: Manual Opening
```bash
# List all reports
dir results\report_*\index.html  # Windows
ls results/report_*/index.html    # Mac/Linux

# Open specific report in browser
start results\report_20240115_143052\index.html  # Windows
open results/report_20240115_143052/index.html   # Mac
```

Option 3: Using the CLI

```bash
# Open the latest report
python cli.py report
```

### Report Customization
Customize report generation in config/test_config.json:
```json
{
  "report_settings": {
    "generate_html": true,
    "include_screenshots": true,
    "include_logs": true,
    "chart_theme": "plotly",
    "report_title": "My Test Results"
  }
}
```

## 🎯 Advanced Usage

### Running Tests in Parallel
```bash
python cli.py run --parallel
```

### Custom Browser Options
Configure browser-specific options in your config file:
```bash
{
  "chrome_options": {
    "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
    "prefs": {
      "download.default_directory": "/path/to/downloads"
    }
  },
  "firefox_options": {
    "args": ["-private"],
    "prefs": {
      "dom.webnotifications.enabled": false
    }
  }
}
```

### 🚀 CI/CD Integration
GitHub Actions `.github/workflows/test.yml`:
```yaml
name: Cross-Browser Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chrome, firefox]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python cli.py run --browsers ${{ matrix.browser }} --headless
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports-${{ matrix.browser }}
        path: results/
```

## 🐛 Troubleshooting
### Common Issues
WebDriver Not Found:
```bash
# Install WebDriver Manager
pip install webdriver-manager
```

Browser Not Detected
- Ensure browser is installed
- Check PATH environment variable
- Run python cli.py browsers to see available browsers

Tests Timing Out
- Increase timeout in config: "timeout": 60
- Check for slow page loads
- Use explicit waits instead of implicit

Permission Errors (Linux/Mac)
```bash
chmod +x chromedriver
chmod +x geckodriver
```

### 🤝 Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### Code Style
- idk just make it look good

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/unit/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:

✅ **You CAN:**
- Use this code for commercial purposes
- Modify and distribute the code
- Use it in private projects
- Sublicense it

📋 **You MUST:**
- Include the original copyright notice
- Include the license text

❌ **You CANNOT:**
- Hold the authors liable for any damages
- Use authors' names for endorsement without permission

### Summary

This is a permissive open-source license that allows you to do almost anything with the code as long as you include the original copyright and license notice in any copy of the software.