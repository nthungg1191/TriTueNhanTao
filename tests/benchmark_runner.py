#!/usr/bin/env python
"""
Benchmark Runner - CLI for Performance Testing
=============================================

Usage:
    python tests/benchmark_runner.py                    # Run all benchmarks
    python tests/benchmark_runner.py --all             # Run all benchmarks
    python tests/benchmark_runner.py --api             # API benchmarks only
    python tests/benchmark_runner.py --face            # Face recognition benchmarks only
    python tests/benchmark_runner.py --load --users 100 # Load test with 100 users
    python tests/benchmark_runner.py --stress           # Stress test
    python tests/benchmark_runner.py --report json      # Output as JSON
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.performance_test import (
    PerformanceBenchmark,
    FaceRecognitionBenchmark,
    DatabaseQueryBenchmark,
    ReportGenerator
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def run_api_benchmarks(args):
    """Run API endpoint benchmarks"""
    print_header("API ENDPOINT BENCHMARKING")

    base_url = args.base_url or 'http://localhost:5555'
    print(f"Target URL: {base_url}\n")

    benchmark = PerformanceBenchmark(base_url=base_url)

    if args.endpoints:
        # Custom endpoints
        endpoints = []
        for ep in args.endpoints:
            parts = ep.split(':')
            if len(parts) == 2:
                endpoints.append({'name': parts[0], 'path': parts[1], 'method': 'GET'})
        benchmark.endpoints = endpoints

    if args.load:
        # Load test mode
        users = args.users or 50
        duration = args.duration or 30

        print(f"Load Test Configuration:")
        print(f"  Concurrent Users: {users}")
        print(f"  Duration: {duration} seconds\n")

        results = []
        for endpoint in benchmark.endpoints:
            print(f"Testing: {endpoint['name']}")
            result = benchmark.run_load_test(endpoint, users, duration)
            results.append(result)
            print(result.summary())
            print()

    elif args.stress:
        # Stress test mode
        start_users = args.start_users or 10
        max_users = args.max_users or 200
        step = args.step or 10
        duration = args.duration or 10

        print(f"Stress Test Configuration:")
        print(f"  Start Users: {start_users}")
        print(f"  Max Users: {max_users}")
        print(f"  Step: {step}")
        print(f"  Duration per step: {duration} seconds\n")

        all_results = []
        for endpoint in benchmark.endpoints:
            print(f"\nTesting: {endpoint['name']}")
            results = benchmark.run_stress_test(
                endpoint,
                start_users=start_users,
                max_users=max_users,
                step=step,
                duration_per_step=duration
            )
            all_results.extend(results)

            print("\n  Scaling Results:")
            print(f"  {'Users':<8} {'Avg Time':<12} {'P95':<12} {'Throughput':<15} {'Errors':<10}")
            print("  " + "-"*57)
            for r in results:
                print(
                    f"  {r.extra_metrics.get('concurrent_users', 0):<8} "
                    f"{r.avg_response_time*1000:<10.2f}ms "
                    f"{r.p95_response_time*1000:<10.2f}ms "
                    f"{r.throughput:<15.2f} "
                    f"{r.error_rate:<10.1f}%"
                )

        return all_results

    else:
        # Standard benchmark mode
        requests = args.requests or 20
        print(f"Running {requests} requests per endpoint\n")

        results = benchmark.run_all_benchmarks(requests_per_endpoint=requests)

        print_header("API BENCHMARK SUMMARY")
        for result in results:
            print(f"\n{result.name}:")
            print(f"  Avg: {result.avg_response_time*1000:.2f}ms | "
                  f"P95: {result.p95_response_time*1000:.2f}ms | "
                  f"Throughput: {result.throughput:.2f} req/s")

        return results


def run_face_recognition_benchmarks(args):
    """Run face recognition benchmarks"""
    print_header("FACE RECOGNITION BENCHMARKING")

    face_benchmark = FaceRecognitionBenchmark()

    if args.face_scale:
        # Scaling test
        scales = [int(s) for s in args.face_scale.split(',')]
        print(f"Testing scales: {scales}\n")
        results = face_benchmark.benchmark_recognition_with_scale(scales=scales)

    elif args.face_cache:
        # Cache efficiency test
        num_requests = args.face_cache_requests or 100
        cache_ttl = args.cache_ttl or 10.0

        print(f"Cache Efficiency Test:")
        print(f"  Number of Requests: {num_requests}")
        print(f"  Cache TTL: {cache_ttl} seconds\n")

        result = face_benchmark.benchmark_cache_efficiency(
            num_requests=num_requests,
            cache_ttl=cache_ttl
        )

        print(f"Cache Hit Rate: {result.get('hit_rate', 0):.1f}%")
        print(f"Average Time: {result.get('avg_time', 0)*1000:.2f}ms")
        print(f"Cache Hits: {result.get('cache_hits', 0)}")
        print(f"Cache Misses: {result.get('cache_misses', 0)}")

        return [result]

    elif args.face_detection:
        # Face detection speed test
        num_tests = args.num_tests or 20

        print(f"Face Detection Speed Test:")
        print(f"  Number of Tests: {num_tests}\n")

        result = face_benchmark.measure_face_detection_speed(num_tests=num_tests)

        if 'error' in result:
            print(f"Note: {result['error']}")
            print("This is expected if face_recognition library is not installed.")
        else:
            print(f"Average Detection Time: {result.get('avg_detection_time', 0)*1000:.2f}ms")
            print(f"Average Encoding Time: {result.get('avg_encoding_time', 0)*1000:.2f}ms")

        return [result]

    else:
        # Default: run all face recognition tests
        print("Running all face recognition benchmarks...\n")

        # Scaling test
        print("1. Recognition Scaling Test")
        scaling_results = face_benchmark.benchmark_recognition_with_scale(
            scales=[10, 50, 100, 200]
        )

        # Cache efficiency
        print("\n2. Cache Efficiency Test")
        cache_result = face_benchmark.benchmark_cache_efficiency(
            num_requests=100,
            cache_ttl=10.0
        )
        print(f"Cache Hit Rate: {cache_result.get('hit_rate', 0):.1f}%")

        return scaling_results + [cache_result]


def run_database_benchmarks(args):
    """Run database query benchmarks"""
    print_header("DATABASE QUERY BENCHMARKING")

    try:
        from app import create_app, db

        app = create_app()
        db_benchmark = DatabaseQueryBenchmark(app=app, db=db)

        print("Running database query benchmarks...\n")

        results = db_benchmark.benchmark_common_queries()

        print(f"{'Query':<30} {'Avg Time':<15} {'P95':<15} {'Errors':<10}")
        print("-"*70)
        for result in results:
            if 'error' in result:
                print(f"{result.get('query_name', 'Unknown'):<30} Error: {result.get('error', 'N/A')}")
            else:
                print(
                    f"{result.get('query_name', 'Unknown'):<30} "
                    f"{result.get('avg_time', 0)*1000:<13.2f}ms "
                    f"{result.get('p95_time', 0)*1000:<13.2f}ms "
                    f"{result.get('num_errors', 0):<10}"
                )

        return results

    except Exception as e:
        print(f"Database benchmark error: {e}")
        print("Make sure the server is running and database is accessible.")
        return []


def run_all_benchmarks(args):
    """Run all benchmark types"""
    all_results = []

    # API benchmarks
    api_results = run_api_benchmarks(args)
    if api_results:
        all_results.extend(api_results if isinstance(api_results, list) else [api_results])

    # Face recognition benchmarks
    face_results = run_face_recognition_benchmarks(args)
    if face_results:
        all_results.extend(face_results if isinstance(face_results, list) else [face_results])

    # Database benchmarks (optional)
    if args.include_db:
        db_results = run_database_benchmarks(args)
        if db_results:
            all_results.extend(db_results if isinstance(db_results, list) else [db_results])

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description='Performance Testing CLI for Attendance System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/benchmark_runner.py --all
  python tests/benchmark_runner.py --api --requests 50
  python tests/benchmark_runner.py --load --users 100 --duration 60
  python tests/benchmark_runner.py --stress --max-users 500
  python tests/benchmark_runner.py --face --face-scale 10,50,100
  python tests/benchmark_runner.py --report json --output results.json
        """
    )

    # Benchmark type
    benchmark_group = parser.add_argument_group('Benchmark Type')
    type_group = benchmark_group.add_mutually_exclusive_group()
    type_group.add_argument('--all', action='store_true', help='Run all benchmarks')
    type_group.add_argument('--api', action='store_true', help='Run API endpoint benchmarks only')
    type_group.add_argument('--face', action='store_true', help='Run face recognition benchmarks only')
    type_group.add_argument('--db', action='store_true', help='Run database benchmarks only')
    type_group.add_argument('--load', action='store_true', help='Run load test mode')
    type_group.add_argument('--stress', action='store_true', help='Run stress test mode')

    # API benchmark options
    api_group = parser.add_argument_group('API Benchmark Options')
    api_group.add_argument('--base-url', type=str, default='http://localhost:5555',
                          help='Base URL for API (default: http://localhost:5555)')
    api_group.add_argument('--requests', type=int, default=20,
                          help='Number of requests per endpoint (default: 20)')
    api_group.add_argument('--users', type=int, default=50,
                          help='Number of concurrent users for load test (default: 50)')
    api_group.add_argument('--duration', type=int, default=30,
                          help='Duration in seconds for load/stress test (default: 30)')
    api_group.add_argument('--start-users', type=int, default=10,
                          help='Starting users for stress test (default: 10)')
    api_group.add_argument('--max-users', type=int, default=200,
                          help='Maximum users for stress test (default: 200)')
    api_group.add_argument('--step', type=int, default=10,
                          help='User increment step for stress test (default: 10)')
    api_group.add_argument('--endpoints', nargs='+',
                          help='Custom endpoints in format: "Name:/path" (e.g., "Test:/api/stats")')

    # Face recognition benchmark options
    face_group = parser.add_argument_group('Face Recognition Options')
    face_group.add_argument('--face-scale', type=str,
                           help='Comma-separated scales for recognition test (e.g., "10,50,100,200")')
    face_group.add_argument('--face-cache', action='store_true',
                           help='Run cache efficiency test')
    face_group.add_argument('--face-cache-requests', type=int, default=100,
                          help='Number of requests for cache test (default: 100)')
    face_group.add_argument('--cache-ttl', type=float, default=10.0,
                          help='Cache TTL in seconds (default: 10)')
    face_group.add_argument('--face-detection', action='store_true',
                           help='Run face detection speed test')
    face_group.add_argument('--num-tests', type=int, default=20,
                          help='Number of tests for face detection (default: 20)')

    # Database options
    db_group = parser.add_argument_group('Database Options')
    db_group.add_argument('--include-db', action='store_true',
                         help='Include database benchmarks in --all mode')

    # Report options
    report_group = parser.add_argument_group('Report Options')
    report_group.add_argument('--report', choices=['text', 'json'], default='text',
                             help='Report format (default: text)')
    report_group.add_argument('--output', type=str,
                             help='Output file path (optional)')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("  PERFORMANCE TESTING SUITE")
    print("  Attendance Management System")
    print("="*70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Determine which benchmarks to run
    if args.all:
        results = run_all_benchmarks(args)
    elif args.api or args.load or args.stress:
        results = run_api_benchmarks(args)
    elif args.face:
        results = run_face_recognition_benchmarks(args)
    elif args.db:
        results = run_database_benchmarks(args)
    else:
        # Default: run API benchmarks
        results = run_api_benchmarks(args)

    # Generate and save report
    if results and args.report == 'json':
        report = json.dumps(results, indent=2, default=str)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nJSON report saved to: {args.output}")
        else:
            print("\n" + report)

    # Summary
    print_header("TEST COMPLETED")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if results:
        # Count successful vs failed
        total = len(results)
        print(f"  Total benchmarks run: {total}")

    print("\nRun with --help for more options.")


if __name__ == '__main__':
    main()
