#!/usr/bin/env python3
"""
PyBoy Benchmark Suite Runner

A unified script to run the entire PyBoy benchmark suite including:
- Performance benchmarks
- Bot support benchmarks
- Game-specific bot strategy tests
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import shutil
import tempfile
import concurrent.futures


def run_command(cmd, cwd=None):
    """Run a command and capture output"""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True,
                                capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return None


def run_benchmark(benchmark_script, args, timeout=None):
    """Run a specific benchmark script with given arguments"""
    cmd = [sys.executable, benchmark_script] + args

    print(f"Running: {' '.join(cmd)}")

    try:
        start_time = time.time()
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start_time

        return {
            "success": True,
            "script": benchmark_script,
            "args": args,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": elapsed
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "script": benchmark_script,
            "args": args,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode,
            "error": str(e)
        }
    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "script": benchmark_script,
            "args": args,
            "stdout": e.stdout if hasattr(e, 'stdout') else None,
            "stderr": e.stderr if hasattr(e, 'stderr') else None,
            "error": f"Timeout after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "script": benchmark_script,
            "args": args,
            "error": str(e)
        }


def find_roms(rom_dir, extensions=None):
    """Find ROM files in the given directory"""
    if extensions is None:
        extensions = ['.gb', '.gbc', '.rom']

    roms = []
    if not os.path.isdir(rom_dir):
        print(f"Warning: ROM directory '{rom_dir}' not found.")
        return roms

    for root, _, files in os.walk(rom_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                roms.append(os.path.join(root, file))

    return roms


def combine_results(results_dir, output_file):
    """Combine all JSON result files into a single report"""
    combined = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {}
    }

    results_path = Path(results_dir)

    # Find all JSON files
    json_files = list(results_path.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            benchmark_name = json_file.stem
            combined["benchmarks"][benchmark_name] = data
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    # Save combined results
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"Combined results saved to: {output_file}")

    return combined


def create_html_report(combined_results, output_file, charts_dir):
    """Create an HTML report from combined results"""
    charts_path = Path(charts_dir)

    # Find all PNG files in charts directory
    chart_files = []
    if charts_path.exists():
        chart_files = list(charts_path.glob("*.png"))

    # Create HTML content
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PyBoy Benchmark Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1, h2, h3 {
                color: #2c3e50;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .chart-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 20px;
            }
            .chart {
                flex: 1;
                min-width: 300px;
                margin-bottom: 20px;
            }
            .chart img {
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .summary {
                margin-bottom: 20px;
                font-size: 18px;
            }
            .timestamp {
                margin-bottom: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PyBoy Benchmark Report</h1>
    """

    # Add timestamp
    timestamp = combined_results.get("timestamp", "Unknown")
    html += f'<div class="timestamp">Generated on: {timestamp}</div>'

    # Add summary
    num_benchmarks = len(combined_results.get("benchmarks", {}))
    html += f"""
    <div class="summary">
        <p>This report contains results from {num_benchmarks} benchmark(s).</p>
    </div>
    """

    # Add charts section
    if chart_files:
        html += """
        <div class="section">
            <h2>Charts</h2>
            <div class="chart-container">
        """

        for chart_file in chart_files:
            chart_name = chart_file.stem.replace('_', ' ').title()
            rel_path = os.path.relpath(chart_file, os.path.dirname(output_file))

            html += f"""
            <div class="chart">
                <h3>{chart_name}</h3>
                <img src="{rel_path}" alt="{chart_name}">
            </div>
            """

        html += """
            </div>
        </div>
        """

    # Add benchmark results
    benchmarks = combined_results.get("benchmarks", {})
    for name, data in benchmarks.items():
        html += f"""
        <div class="section">
            <h2>{name}</h2>
        """

        # Create table for simple data
        html += create_results_table(data)

        html += """
        </div>
        """

    # Close HTML
    html += """
        </div>
    </body>
    </html>
    """

    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"HTML report saved to: {output_file}")


def create_results_table(data, max_depth=2, current_depth=0):
    """Create an HTML table from nested data"""
    if current_depth >= max_depth or not isinstance(data, dict):
        return f"<pre>{json.dumps(data, indent=2)}</pre>"

    html = "<table>"

    # Add table headers
    html += "<tr><th>Key</th><th>Value</th></tr>"

    # Add table rows
    for key, value in data.items():
        if isinstance(value, dict) and current_depth < max_depth - 1:
            html += f"<tr><td>{key}</td><td>{create_results_table(value, max_depth, current_depth + 1)}</td></tr>"
        else:
            # Format value based on type
            if isinstance(value, (list, dict)):
                formatted_value = f"<pre>{json.dumps(value, indent=2)}</pre>"
            elif isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)

            html += f"<tr><td>{key}</td><td>{formatted_value}</td></tr>"

    html += "</table>"
    return html


def copy_scripts_to_dir(target_dir):
    """Copy benchmark scripts to target directory"""
    # Create directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Define scripts to copy
    scripts = {
        "benchmark_suite.py": """#!/usr/bin/env python3
# PyBoy Benchmark Suite
# A comprehensive benchmarking tool for the PyBoy Game Boy emulator
""",
        "bot_support.py": """#!/usr/bin/env python3
# PyBoy Bot Support Benchmark
# Tests bot capabilities and performance
""",
        "bot_strategies.py": """#!/usr/bin/env python3
# PyBoy Game-Specific Bot Strategies
# A collection of game-specific bot implementations
"""
    }

    # Copy scripts if they exist, otherwise create placeholder
    script_paths = {}

    for script_name, placeholder in scripts.items():
        # First check if script exists in current directory
        if os.path.exists(script_name):
            shutil.copy(script_name, os.path.join(target_dir, script_name))
            script_paths[script_name] = os.path.join(target_dir, script_name)
        else:
            # Create placeholder file
            script_path = os.path.join(target_dir, script_name)
            with open(script_path, 'w') as f:
                f.write(placeholder)
            script_paths[script_name] = script_path
            print(f"Warning: {script_name} not found, created placeholder at {script_path}")

    return script_paths


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='PyBoy Benchmark Suite Runner')

    parser.add_argument('--rom-dir', type=str, default='roms',
                        help='Directory containing Game Boy ROM files')
    parser.add_argument('--output-dir', type=str, default='benchmark_results',
                        help='Directory to store all benchmark results')
    parser.add_argument('--headless', action='store_true',
                        help='Run in headless mode (no window)')
    parser.add_argument('--skip-performance', action='store_true',
                        help='Skip performance benchmarks')
    parser.add_argument('--skip-bot-support', action='store_true',
                        help='Skip bot support benchmarks')
    parser.add_argument('--skip-bot-strategies', action='store_true',
                        help='Skip bot strategy tests')
    parser.add_argument('--parallel', action='store_true',
                        help='Run benchmarks in parallel when possible')
    parser.add_argument('--timeout', type=int, default=1800,
                        help='Timeout for each benchmark in seconds (default: 30 minutes)')

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Create output directories
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    results_dir = output_dir / "results"
    results_dir.mkdir(exist_ok=True)

    charts_dir = output_dir / "charts"
    charts_dir.mkdir(exist_ok=True)

    # Create temp directory for scripts
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy or create benchmark scripts
        scripts = copy_scripts_to_dir(temp_dir)

        # Find ROMs
        roms = find_roms(args.rom_dir)
        if not roms:
            print(f"No ROM files found in '{args.rom_dir}'. Please provide valid ROM files.")
            return 1

        print(f"Found {len(roms)} ROM files.")

        # Select a representative ROM for benchmarks
        test_rom = roms[0]
        print(f"Using {test_rom} for basic benchmarks.")

        # Store benchmark results
        benchmark_results = {}

        # Common arguments
        headless_arg = ['--headless'] if args.headless else []

        # Run benchmarks
        if args.parallel:
            # Prepare benchmark tasks
            tasks = []

            if not args.skip_performance:
                performance_args = [test_rom, '--output', str(results_dir / 'performance_results.json'),
                                    '--charts', str(charts_dir)] + headless_arg
                tasks.append((scripts['benchmark_suite.py'], performance_args, args.timeout))

            if not args.skip_bot_support:
                bot_support_args = [test_rom, '--output', str(results_dir / 'bot_support_results.json'),
                                    '--charts', str(charts_dir)] + headless_arg
                tasks.append((scripts['bot_support.py'], bot_support_args, args.timeout))

            if not args.skip_bot_strategies:
                # Use all compatible ROMs for bot strategies
                bot_strategy_args = roms + ['--output', str(results_dir / 'bot_strategy_results.json'),
                                            '--charts', str(charts_dir), '--frames', '500'] + headless_arg
                tasks.append((scripts['bot_strategies.py'], bot_strategy_args, args.timeout))

            # Run tasks in parallel
            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = [executor.submit(run_benchmark, script, script_args, timeout)
                           for script, script_args, timeout in tasks]

                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    result = future.result()
                    script_name = Path(tasks[i][0]).stem
                    benchmark_results[script_name] = result

                    print(f"Completed: {script_name}")
                    if not result['success']:
                        print(f"  Error: {result.get('error', 'Unknown error')}")
        else:
            # Run benchmarks sequentially
            if not args.skip_performance:
                performance_args = [test_rom, '--output', str(results_dir / 'performance_results.json'),
                                    '--charts', str(charts_dir)] + headless_arg
                result = run_benchmark(scripts['benchmark_suite.py'], performance_args, args.timeout)
                benchmark_results['benchmark_suite'] = result

                print(f"Completed: benchmark_suite")
                if not result['success']:
                    print(f"  Error: {result.get('error', 'Unknown error')}")

            if not args.skip_bot_support:
                bot_support_args = [test_rom, '--output', str(results_dir / 'bot_support_results.json'),
                                    '--charts', str(charts_dir)] + headless_arg
                result = run_benchmark(scripts['bot_support.py'], bot_support_args, args.timeout)
                benchmark_results['bot_benchmark'] = result

                print(f"Completed: bot_benchmark")
                if not result['success']:
                    print(f"  Error: {result.get('error', 'Unknown error')}")

            if not args.skip_bot_strategies:
                # Use all compatible ROMs for bot strategies
                bot_strategy_args = roms + ['--output', str(results_dir / 'bot_strategy_results.json'),
                                            '--charts', str(charts_dir), '--frames', '500'] + headless_arg
                result = run_benchmark(scripts['bot_strategies.py'], bot_strategy_args, args.timeout)
                benchmark_results['bot_strategies'] = result

                print(f"Completed: bot_strategies")
                if not result['success']:
                    print(f"  Error: {result.get('error', 'Unknown error')}")

        # Save benchmark execution results
        with open(results_dir / 'benchmark_execution_results.json', 'w') as f:
            json.dump(benchmark_results, f, indent=2)

        # Combine all results
        combined_results = combine_results(results_dir, output_dir / 'combined_results.json')

        # Create HTML report
        create_html_report(combined_results, output_dir / 'benchmark_report.html', charts_dir)

    print("\nBenchmark suite completed!")
    print(f"Results are available in the '{output_dir}' directory.")
    print(f"Check '{output_dir}/benchmark_report.html' for a complete report.")

    return 0


if __name__ == "__main__":
    sys.exit(main())