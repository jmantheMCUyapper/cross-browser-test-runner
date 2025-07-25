#!/usr/bin/env python3
"""
Cross-Browser Test Runner CLI
A professional command-line interface for the test automation framework
"""
import click
import sys
import os
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.test_runner import TestRunner
from src.browser_manager import BrowserManager

console = Console()


@click.group()
@click.version_option(version='1.0.0', prog_name='Cross-Browser Test Runner')
def cli():
    """🚀 Cross-Browser Test Automation Framework

    A professional test automation framework for running Selenium tests
    across multiple browsers with beautiful HTML reports.
    """
    pass


@cli.command()
def browsers():
    """List available browsers on this system"""
    with console.status("[bold green]Detecting browsers...") as status:
        browser_manager = BrowserManager()
        available = browser_manager.available_browsers

    table = Table(title="Available Browsers", show_header=True, header_style="bold magenta")
    table.add_column("Browser", style="cyan", width=12)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Driver", width=20)

    for browser, is_available in available.items():
        status = "✅ Available" if is_available else "❌ Not Found"
        status_color = "green" if is_available else "red"
        driver_info = "WebDriver Ready" if is_available else "Driver Missing"
        table.add_row(browser.title(), f"[{status_color}]{status}[/{status_color}]", driver_info)

    console.print(table)


@cli.command()
@click.option('--config', '-c', default='config/test_config.json',
              help='Path to test configuration file')
@click.option('--browsers', '-b', multiple=True,
              help='Specific browsers to test (can specify multiple)')
@click.option('--tests', '-t', multiple=True,
              help='Specific test files to run')
@click.option('--parallel', '-p', is_flag=True,
              help='Run tests in parallel')
@click.option('--headless', '-h', is_flag=True,
              help='Run browsers in headless mode')
@click.option('--open-report', '-o', is_flag=True,
              help='Open HTML report after completion')
def run(config, browsers, tests, parallel, headless, open_report):
    """Run cross-browser tests"""

    # Display run configuration
    panel_content = f"""
[bold cyan]Test Configuration:[/bold cyan]
├─ Config File: {config}
├─ Browsers: {', '.join(browsers) if browsers else 'All configured'}
├─ Tests: {', '.join(tests) if tests else 'All configured'}
├─ Parallel: {'Yes' if parallel else 'No'}
└─ Headless: {'Yes' if headless else 'No'}
    """
    console.print(Panel(panel_content, title="🚀 Starting Test Run", border_style="green"))

    # Override config if needed
    if browsers or tests or headless:
        with open(config, 'r') as f:
            config_data = json.load(f)

        if browsers:
            config_data['browsers'] = list(browsers)
        if tests:
            config_data['test_files'] = list(tests)
        if headless:
            config_data['headless'] = True

        # Save temporary config
        temp_config = config + '.tmp'
        with open(temp_config, 'w') as f:
            json.dump(config_data, f)
        config = temp_config

    try:
        # Run tests with progress indicator
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("[green]Running tests...", total=None)

            runner = TestRunner(config)
            results = runner.run_tests()

            progress.update(task, completed=True)

        # Display results summary
        _display_results_summary(results)

        # Open report if requested
        if open_report:
            import webbrowser
            reports_dir = Path("results")
            latest_report = max(reports_dir.glob("report_*/index.html"),
                                key=os.path.getctime, default=None)
            if latest_report:
                console.print(f"\n[bold green]Opening report in browser: {latest_report}")
                webbrowser.open(f"file://{latest_report.absolute()}")

    finally:
        # Clean up temp config
        if config.endswith('.tmp') and os.path.exists(config):
            os.remove(config)


@cli.command()
def init():
    """Initialize a new test project with example files"""
    console.print("[bold green]Initializing new cross-browser test project...")

    # Create directory structure
    directories = [
        "tests",
        "config",
        "src",
        "results",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        console.print(f"✅ Created directory: {directory}")

    # Create default config
    default_config = {
        "browsers": ["chrome", "firefox", "edge"],
        "test_files": ["tests/"],
        "parallel_execution": False,
        "headless": False,
        "timeout": 30
    }

    with open("config/test_config.json", "w") as f:
        json.dump(default_config, f, indent=2)
    console.print("✅ Created default configuration")

    # Create example test
    example_test = '''"""Example test file"""
import pytest
from selenium.webdriver.common.by import By


def test_example(browser):
    """Example test case"""
    browser.get("https://www.example.com")
    assert "Example Domain" in browser.title

    # Find and verify heading
    heading = browser.find_element(By.TAG_NAME, "h1")
    assert heading.text == "Example Domain"
'''

    with open("tests/test_example.py", "w") as f:
        f.write(example_test)
    console.print("✅ Created example test file")

    console.print("\n[bold green]Project initialized successfully!")
    console.print("Run 'python cli.py run' to execute tests")


@cli.command()
def report():
    """Open the latest test report"""
    import webbrowser

    reports_dir = Path("results")
    if not reports_dir.exists():
        console.print("[red]No results directory found!")
        return

    reports = list(reports_dir.glob("report_*/index.html"))
    if not reports:
        console.print("[red]No reports found!")
        return

    latest_report = max(reports, key=os.path.getctime)
    console.print(f"[green]Opening latest report: {latest_report}")
    webbrowser.open(f"file://{latest_report.absolute()}")


def _display_results_summary(results):
    """Display test results summary in a nice format"""
    total = len(results['results'])
    passed = sum(1 for r in results['results'] if r['status'] == 'passed')
    failed = sum(1 for r in results['results'] if r['status'] == 'failed')
    skipped = sum(1 for r in results['results'] if r['status'] == 'skipped')

    # Create summary table
    table = Table(title="Test Results Summary", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Total Tests", str(total))
    table.add_row("Passed", f"[green]{passed}[/green]")
    table.add_row("Failed", f"[red]{failed}[/red]")
    table.add_row("Skipped", f"[yellow]{skipped}[/yellow]")
    table.add_row("Pass Rate", f"{(passed / total * 100 if total > 0 else 0):.1f}%")
    table.add_row("Duration", f"{results['total_duration']:.2f}s")

    console.print("\n")
    console.print(table)

    # Show failed tests if any
    if failed > 0:
        console.print("\n[bold red]Failed Tests:[/bold red]")
        for result in results['results']:
            if result['status'] == 'failed':
                console.print(f"  ❌ {result['browser']}: {result['test_file']}::{result['test_name']}")
                if result.get('error_message'):
                    console.print(f"     → {result['error_message'][:80]}...")


if __name__ == '__main__':
    cli()