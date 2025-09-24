import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add this import
from src.report_generator import ReportGenerator


class TestRunner:
    def __init__(self, config_path: str = "config/test_config.json"):
        self.config = self._load_config(config_path)
        self.results = []
        self.start_time = None
        self.end_time = None

    def _load_config(self, config_path: str) -> dict:
        """Load test configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)

    def run_tests(self) -> Dict[str, Any]:
        """Run all configured tests"""
        from src.browser_manager import BrowserManager
        import pytest

        self.start_time = time.time()
        headless_mode = bool(self.config.get("headless", False))
        browser_manager = BrowserManager(headless_override=headless_mode)
        browser_versions = {}

        # Get available browsers
        available_browsers = browser_manager.available_browsers
        print(f"\nAvailable browsers: {available_browsers}")

        # Filter to only available browsers
        available_browser_list = [b for b, available in available_browsers.items() if available]

        # Store browser versions
        for browser in available_browser_list:
            try:
                driver = browser_manager.get_browser(browser)
                if driver:
                    browser_versions[browser] = driver.capabilities.get('browserVersion', 'Unknown')
                    driver.quit()
            except Exception as e:
                print(f"Error getting version for {browser}: {e}")
                browser_versions[browser] = "Unknown"

        # Run tests for each browser
        headless_mode = bool(self.config.get("headless", False))
    
        for browser in self.config.get("browsers", ["chrome"]):
            if browser not in available_browser_list:
                print(f"\nSkipping {browser} - not available")
                # Add skipped results for this browser
                for test_file in self.config.get("test_files", []):
                    self.results.append({
                        "browser": browser,
                        "test_file": Path(test_file).stem,
                        "test_name": "all_tests",
                        "duration": None,
                        "status": "skipped",
                        "error": None,
                        "error_message": f"{browser} browser not available"
                    })
                continue

            print(f"\nRunning tests on {browser}...")

            # Run pytest for this browser
            test_files = self.config.get("test_files", ["tests/"])
            for test_file in test_files:
                if Path(test_file).exists():
                    result = self._run_test_file(test_file, browser, headless=headless_mode)
                    self.results.extend(result)
                else:
                    print(f"Warning: Test file not found: {test_file}")

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        # Compile final results
        final_results = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "browser_versions": browser_versions,
            "results": self.results
        }

        # Generate HTML report
        report_generator = ReportGenerator()
        report_path = report_generator.generate_report(final_results)
        print(f"\nHTML Report generated: {report_path}")

        return final_results

    def _run_test_file(self, test_file: str, browser: str, headless: bool = False,
    ) -> List[Dict[str, Any]]:
        """Run a specific test file with a specific browser"""
        import subprocess
        import xml.etree.ElementTree as ET
        from pathlib import Path
        import tempfile
        import os

        # Create temporary result file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            result_file = tmp.name

        # Run pytest with JUnit XML output
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            f"--browser={browser}",
            f"--junitxml={result_file}",
            "-v",
            "--tb=short"  # Shorter traceback format
        ]

        if headless:
            cmd.append("--headless")
        results = []
        try:
            # Run the tests
            process = subprocess.run(cmd, capture_output=True, text=True)
            print(f"\nTest output for {browser} - {test_file}:")
            print(process.stdout[-500:] if len(process.stdout) > 500 else process.stdout)  # Last 500 chars
            if process.stderr:
                print(f"Test errors:\n{process.stderr}")

        except Exception as e:
            print(f"Error running tests: {e}")
            # Add error result
            results.append({
                "browser": browser,
                "test_file": Path(test_file).stem,
                "test_name": "test_execution",
                "duration": 0,
                "status": "failed",
                "error": type(e).__name__,
                "error_message": str(e)
            })
            return results

        # Parse results
        try:
            if os.path.exists(result_file) and os.path.getsize(result_file) > 0:
                tree = ET.parse(result_file)
                root = tree.getroot()

                # Get test suite information
                testsuite = root.find('testsuite') or root
                if testsuite is not None:
                    # Parse individual test cases
                    testcases = testsuite.findall('.//testcase')

                    if testcases:
                        for testcase in testcases:
                            result = {
                                "browser": browser,
                                "test_file": Path(test_file).stem,
                                "test_name": testcase.get("name", "unknown"),
                                "duration": float(testcase.get("time", 0)),
                                "status": "passed",
                                "error": None,
                                "error_message": None
                            }

                            # Check for failures
                            failure = testcase.find("failure")
                            if failure is not None:
                                result["status"] = "failed"
                                result["error"] = failure.get("type", "Unknown")
                                result["error_message"] = failure.get("message", "") or failure.text

                            # Check for errors
                            error = testcase.find("error")
                            if error is not None:
                                result["status"] = "failed"
                                result["error"] = error.get("type", "Unknown")
                                result["error_message"] = error.get("message", "") or error.text

                            # Check for skips
                            skipped = testcase.find("skipped")
                            if skipped is not None:
                                result["status"] = "skipped"
                                result["error_message"] = skipped.get("message", "")

                            results.append(result)
                    else:
                        # No individual test cases, create summary from testsuite attributes
                        tests = int(testsuite.get('tests', 0))
                        failures = int(testsuite.get('failures', 0))
                        skipped = int(testsuite.get('skipped', 0))
                        time_taken = float(testsuite.get('time', 0))

                        if tests == 0:
                            status = 'skipped'
                        elif failures > 0:
                            status = 'failed'
                        else:
                            status = 'passed'

                        results.append({
                            "browser": browser,
                            "test_file": Path(test_file).stem,
                            "test_name": "all_tests",
                            "duration": time_taken,
                            "status": status,
                            "error": None,
                            "error_message": None
                        })
            else:
                # No results file or empty file
                print(f"No XML results file found at {result_file} or file is empty")
                # Parse stdout for pass/fail
                stdout = process.stdout.lower()
                if "passed" in stdout and "failed" not in stdout:
                    status = "passed"
                elif "failed" in stdout:
                    status = "failed"
                else:
                    status = "unknown"

                results.append({
                    "browser": browser,
                    "test_file": Path(test_file).stem,
                    "test_name": "all_tests",
                    "duration": 0,
                    "status": status,
                    "error": None,
                    "error_message": f"Exit code: {process.returncode}"
                })

        except Exception as e:
            print(f"Error parsing results: {e}")
            results.append({
                "browser": browser,
                "test_file": Path(test_file).stem,
                "test_name": "result_parsing",
                "duration": 0,
                "status": "failed",
                "error": type(e).__name__,
                "error_message": str(e)
            })
        finally:
            # Clean up temp file
            try:
                if os.path.exists(result_file):
                    os.unlink(result_file)
            except:
                pass

        # If no results were captured, add a default entry
        if not results:
            results.append({
                "browser": browser,
                "test_file": Path(test_file).stem,
                "test_name": "unknown",
                "duration": 0,
                "status": "unknown",
                "error": None,
                "error_message": "No test results captured"
            })

        return results