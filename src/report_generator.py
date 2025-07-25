import os
import json
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jinja2 import Template
import pandas as pd
from typing import Dict, List, Any


class ReportGenerator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report with visualizations"""
        # Create report directory
        report_dir = self.results_dir / f"report_{self.timestamp}"
        report_dir.mkdir(exist_ok=True)

        # Generate charts
        charts = self._generate_charts(test_results, report_dir)

        # Generate HTML report
        report_path = report_dir / "index.html"
        self._generate_html_report(test_results, charts, report_path)

        # Save raw results as JSON
        json_path = report_dir / "results.json"
        with open(json_path, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)

        return str(report_path)

    def _generate_charts(self, test_results: Dict[str, Any], report_dir: Path) -> Dict[str, str]:
        """Generate various charts for the report"""
        charts = {}

        # 1. Overall Pass/Fail Pie Chart
        charts['overall_pie'] = self._create_overall_pie_chart(test_results)

        # 2. Browser Comparison Bar Chart
        charts['browser_comparison'] = self._create_browser_comparison_chart(test_results)

        # 3. Test Duration Timeline
        charts['duration_timeline'] = self._create_duration_timeline(test_results)

        # 4. Test Suite Summary
        charts['suite_summary'] = self._create_suite_summary_chart(test_results)

        # 5. Error Distribution
        charts['error_distribution'] = self._create_error_distribution_chart(test_results)

        return charts

    def _create_overall_pie_chart(self, test_results: Dict[str, Any]) -> str:
        """Create pie chart showing overall pass/fail ratio"""
        passed = sum(1 for result in test_results['results'] if result['status'] == 'passed')
        failed = sum(1 for result in test_results['results'] if result['status'] == 'failed')
        skipped = sum(1 for result in test_results['results'] if result['status'] == 'skipped')

        fig = go.Figure(data=[go.Pie(
            labels=['Passed', 'Failed', 'Skipped'],
            values=[passed, failed, skipped],
            hole=.3,
            marker_colors=['#28a745', '#dc3545', '#ffc107']
        )])

        fig.update_layout(
            title="Overall Test Results",
            showlegend=True,
            height=400
        )

        return fig.to_html(div_id="overall_pie", include_plotlyjs='cdn')

    def _create_browser_comparison_chart(self, test_results: Dict[str, Any]) -> str:
        """Create bar chart comparing results across browsers"""
        browser_stats = {}

        for result in test_results['results']:
            browser = result['browser']
            if browser not in browser_stats:
                browser_stats[browser] = {'passed': 0, 'failed': 0, 'skipped': 0}
            browser_stats[browser][result['status']] += 1

        browsers = list(browser_stats.keys())
        passed = [browser_stats[b]['passed'] for b in browsers]
        failed = [browser_stats[b]['failed'] for b in browsers]
        skipped = [browser_stats[b]['skipped'] for b in browsers]

        fig = go.Figure(data=[
            go.Bar(name='Passed', x=browsers, y=passed, marker_color='#28a745'),
            go.Bar(name='Failed', x=browsers, y=failed, marker_color='#dc3545'),
            go.Bar(name='Skipped', x=browsers, y=skipped, marker_color='#ffc107')
        ])

        fig.update_layout(
            title="Test Results by Browser",
            xaxis_title="Browser",
            yaxis_title="Number of Tests",
            barmode='group',
            height=400
        )

        return fig.to_html(div_id="browser_comparison", include_plotlyjs='cdn')

    def _create_duration_timeline(self, test_results: Dict[str, Any]) -> str:
        """Create timeline showing test durations"""
        # Prepare data for timeline
        timeline_data = []
        for result in test_results['results']:
            if result['duration'] is not None:
                timeline_data.append({
                    'Test': f"{result['test_file']}::{result['test_name']}",
                    'Browser': result['browser'],
                    'Duration': result['duration'],
                    'Status': result['status']
                })

        if not timeline_data:
            return "<p>No duration data available</p>"

        df = pd.DataFrame(timeline_data)

        # Create scatter plot
        fig = px.scatter(df, x='Duration', y='Test', color='Browser',
                         symbol='Status', title='Test Execution Duration',
                         labels={'Duration': 'Duration (seconds)'},
                         height=max(400, len(timeline_data) * 30))

        fig.update_traces(marker_size=10)
        fig.update_layout(showlegend=True)

        return fig.to_html(div_id="duration_timeline", include_plotlyjs='cdn')

    def _create_suite_summary_chart(self, test_results: Dict[str, Any]) -> str:
        """Create summary chart by test suite"""
        suite_stats = {}

        for result in test_results['results']:
            suite = result['test_file']
            if suite not in suite_stats:
                suite_stats[suite] = {'passed': 0, 'failed': 0, 'skipped': 0}
            suite_stats[suite][result['status']] += 1

        # Create stacked bar chart
        suites = list(suite_stats.keys())
        passed = [suite_stats[s]['passed'] for s in suites]
        failed = [suite_stats[s]['failed'] for s in suites]
        skipped = [suite_stats[s]['skipped'] for s in suites]

        fig = go.Figure(data=[
            go.Bar(name='Passed', x=suites, y=passed, marker_color='#28a745'),
            go.Bar(name='Failed', x=suites, y=failed, marker_color='#dc3545'),
            go.Bar(name='Skipped', x=suites, y=skipped, marker_color='#ffc107')
        ])

        fig.update_layout(
            title="Test Results by Suite",
            xaxis_title="Test Suite",
            yaxis_title="Number of Tests",
            barmode='stack',
            height=400
        )

        return fig.to_html(div_id="suite_summary", include_plotlyjs='cdn')

    def _create_error_distribution_chart(self, test_results: Dict[str, Any]) -> str:
        """Create chart showing error distribution"""
        error_types = {}

        for result in test_results['results']:
            if result['status'] == 'failed' and result.get('error'):
                error_type = result['error'].split(':')[0].split('.')[-1]
                error_types[error_type] = error_types.get(error_type, 0) + 1

        if not error_types:
            return "<p>No errors to display</p>"

        fig = go.Figure(data=[go.Bar(
            x=list(error_types.keys()),
            y=list(error_types.values()),
            marker_color='#dc3545'
        )])

        fig.update_layout(
            title="Error Type Distribution",
            xaxis_title="Error Type",
            yaxis_title="Count",
            height=400
        )

        return fig.to_html(div_id="error_distribution", include_plotlyjs='cdn')

    def _generate_html_report(self, test_results: Dict[str, Any], charts: Dict[str, str], report_path: Path):
        """Generate the final HTML report"""
        template = Template(self._get_html_template())

        # Calculate summary statistics
        total_tests = len(test_results['results'])
        passed = sum(1 for r in test_results['results'] if r['status'] == 'passed')
        failed = sum(1 for r in test_results['results'] if r['status'] == 'failed')
        skipped = sum(1 for r in test_results['results'] if r['status'] == 'skipped')
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

        # Group results by browser
        results_by_browser = {}
        for result in test_results['results']:
            browser = result['browser']
            if browser not in results_by_browser:
                results_by_browser[browser] = []
            results_by_browser[browser].append(result)

        # Render template
        html_content = template.render(
            title="Cross-Browser Test Report",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary={
                'total': total_tests,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': pass_rate,
                'duration': test_results.get('total_duration', 0),
                'browsers': list(test_results.get('browser_versions', {}).keys())
            },
            browser_versions=test_results.get('browser_versions', {}),
            results_by_browser=results_by_browser,
            charts=charts,
            test_results=test_results
        )

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _get_html_template(self) -> str:
        """Get the HTML template for the report"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .metric-card {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-2px); }
        .metric-value { font-size: 2.5rem; font-weight: bold; }
        .metric-label { color: #6c757d; font-size: 0.9rem; }
        .status-passed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-skipped { color: #ffc107; }
        .chart-container { margin: 20px 0; }
        .test-details { margin-top: 20px; }
        .error-trace { 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
        }
        .navbar-brand { font-weight: bold; }
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            margin-bottom: 30px;
        }
    </style>
</head>
<script>
    // Initialize AOS animations
    AOS.init({
        duration: 800,
        once: true
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
</script>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <i class="fas fa-vial"></i> Cross-Browser Test Report
            </a>
            <span class="navbar-text">
                Generated: {{ timestamp }}
            </span>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero-section">
        <div class="container">
            <h1 class="display-4">Test Execution Report</h1>
            <p class="lead">Comprehensive cross-browser test results and analytics</p>
        </div>
    </div>

    <div class="container">
        <!-- Summary Metrics -->
        <div class="row">
            <div class="col-md-3">
                <div class="metric-card bg-light">
                    <div class="metric-value">{{ summary.total }}</div>
                    <div class="metric-label">TOTAL TESTS</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card bg-light">
                    <div class="metric-value status-passed">{{ summary.passed }}</div>
                    <div class="metric-label">PASSED</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card bg-light">
                    <div class="metric-value status-failed">{{ summary.failed }}</div>
                    <div class="metric-label">FAILED</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card bg-light">
                    <div class="metric-value">{{ "%.1f"|format(summary.pass_rate) }}%</div>
                    <div class="metric-label">PASS RATE</div>
                </div>
            </div>
        </div>

        <!-- Browser Information -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-globe"></i> Browser Versions</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for browser, version in browser_versions.items() %}
                    <div class="col-md-4">
                        <strong>{{ browser }}:</strong> {{ version }}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <div class="chart-container">
                            {{ charts.overall_pie|safe }}
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <div class="chart-container">
                            {{ charts.browser_comparison|safe }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <div class="chart-container">
                            {{ charts.suite_summary|safe }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
'''