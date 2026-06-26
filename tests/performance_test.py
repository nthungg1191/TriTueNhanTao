"""
Performance Testing Module for Attendance Management System
===========================================================

This module provides comprehensive performance testing capabilities including:
- API Benchmarking
- Load Testing
- Stress Testing
- Face Recognition Performance Tests
- Database Query Metrics

Usage:
    from tests.performance_test import PerformanceBenchmark, FaceRecognitionBenchmark

    # Run API benchmarks
    benchmark = PerformanceBenchmark(base_url='http://localhost:5555')
    results = benchmark.run_all_benchmarks()

    # Run face recognition benchmarks
    face_benchmark = FaceRecognitionBenchmark()
    results = face_benchmark.benchmark_recognition_with_scale()
"""

import time
import json
import statistics
import threading
import gc
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


@dataclass
class BenchmarkResult:
    """Container for benchmark results"""
    name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float  # requests per second
    duration: float  # total duration in seconds
    memory_before: float = 0.0
    memory_after: float = 0.0
    memory_delta: float = 0.0
    cpu_before: float = 0.0
    cpu_after: float = 0.0
    extra_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Requests: {self.successful_requests}/{self.total_requests} successful\n"
            f"  Error Rate: {self.error_rate:.2f}%\n"
            f"  Avg Response: {self.avg_response_time*1000:.2f}ms\n"
            f"  P95 Response: {self.p95_response_time*1000:.2f}ms\n"
            f"  Throughput: {self.throughput:.2f} req/s\n"
            f"  Duration: {self.duration:.2f}s"
        )


class SystemMetrics:
    """Track system resource usage"""

    @staticmethod
    def get_memory_mb() -> float:
        if not PSUTIL_AVAILABLE:
            return 0.0
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    @staticmethod
    def get_cpu_percent() -> float:
        if not PSUTIL_AVAILABLE:
            return 0.0
        return psutil.cpu_percent(interval=0.1)

    @staticmethod
    def get_process_count() -> int:
        if not PSUTIL_AVAILABLE:
            return 0
        return len(psutil.Process().children(recursive=True))


class PerformanceBenchmark:
    """
    Main performance benchmarking class for API endpoints
    """

    DEFAULT_ENDPOINTS = [
        {'name': 'List Employees', 'path': '/api/employees', 'method': 'GET'},
        {'name': 'Today Attendance', 'path': '/api/attendance/today', 'method': 'GET'},
        {'name': 'System Stats', 'path': '/api/stats', 'method': 'GET'},
        {'name': 'Face Statistics', 'path': '/api/face/statistics', 'method': 'GET'},
    ]

    def __init__(
        self,
        base_url: str = 'http://localhost:5555',
        auth_token: str = None,
        endpoints: List[Dict] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.endpoints = endpoints or self.DEFAULT_ENDPOINTS
        self.session = None

        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            if auth_token:
                self.session.headers.update({'Authorization': f'Bearer {auth_token}'})

    def _make_request(self, endpoint: Dict) -> Tuple[float, bool, Any]:
        """Make a single request and return (response_time, success, response_data)"""
        if not REQUESTS_AVAILABLE:
            return 0.0, False, {'error': 'requests library not available'}

        url = f"{self.base_url}{endpoint['path']}"
        start_time = time.perf_counter()

        try:
            if endpoint['method'] == 'GET':
                response = self.session.get(url, timeout=30)
            elif endpoint['method'] == 'POST':
                response = self.session.post(url, timeout=30)
            else:
                response = self.session.request(endpoint['method'], url, timeout=30)

            elapsed = time.perf_counter() - start_time
            success = response.status_code < 400

            try:
                data = response.json()
            except:
                data = {'raw': response.text[:100]}

            return elapsed, success, data

        except requests.exceptions.Timeout:
            return time.perf_counter() - start_time, False, {'error': 'Timeout'}
        except requests.exceptions.ConnectionError:
            return time.perf_counter() - start_time, False, {'error': 'Connection Error'}
        except Exception as e:
            return time.perf_counter() - start_time, False, {'error': str(e)}

    def measure_endpoint(
        self,
        endpoint: Dict,
        num_requests: int = 10,
        warmup: int = 2
    ) -> BenchmarkResult:
        """Measure performance of a single endpoint"""

        # Warmup requests
        for _ in range(warmup):
            self._make_request(endpoint)

        response_times = []
        errors = []

        start_time = time.time()
        memory_before = SystemMetrics.get_memory_mb()
        cpu_before = SystemMetrics.get_cpu_percent()

        for _ in range(num_requests):
            elapsed, success, data = self._make_request(endpoint)
            response_times.append(elapsed)
            if not success:
                errors.append(data)

        duration = time.time() - start_time
        memory_after = SystemMetrics.get_memory_mb()
        cpu_after = SystemMetrics.get_cpu_percent()

        successful = num_requests - len(errors)
        error_rate = (len(errors) / num_requests) * 100 if num_requests > 0 else 0

        sorted_times = sorted(response_times)
        p50_idx = int(len(sorted_times) * 0.50)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        return BenchmarkResult(
            name=endpoint['name'],
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=len(errors),
            error_rate=error_rate,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p50_response_time=sorted_times[p50_idx] if sorted_times else 0,
            p95_response_time=sorted_times[p95_idx] if sorted_times else 0,
            p99_response_time=sorted_times[p99_idx] if sorted_times else 0,
            throughput=successful / duration if duration > 0 else 0,
            duration=duration,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_after - memory_before,
            cpu_before=cpu_before,
            cpu_after=cpu_after,
            extra_metrics={'errors': errors[:5]} if errors else {}
        )

    def run_load_test(
        self,
        endpoint: Dict,
        concurrent_users: int,
        duration_seconds: int = 30
    ) -> BenchmarkResult:
        """
        Run load test with specified concurrent users
        """
        if not REQUESTS_AVAILABLE:
            return self._mock_result(endpoint['name'], concurrent_users, duration_seconds)

        response_times = []
        errors = []
        request_count = 0
        stop_event = threading.Event()

        def worker():
            while not stop_event.is_set():
                elapsed, success, data = self._make_request(endpoint)
                response_times.append(elapsed)
                if not success:
                    errors.append(data)

        memory_before = SystemMetrics.get_memory_mb()
        cpu_before = SystemMetrics.get_cpu_percent()

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]

            time.sleep(duration_seconds)
            stop_event.set()

            for future in futures:
                try:
                    future.result(timeout=5)
                except:
                    pass

        duration = duration_seconds
        successful = len(response_times) - len(errors)
        total_requests = len(response_times)
        error_rate = (len(errors) / total_requests * 100) if total_requests > 0 else 0

        sorted_times = sorted(response_times)
        p50_idx = int(len(sorted_times) * 0.50)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)

        memory_after = SystemMetrics.get_memory_mb()
        cpu_after = SystemMetrics.get_cpu_percent()

        return BenchmarkResult(
            name=f"{endpoint['name']} (Load Test: {concurrent_users} users)",
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=len(errors),
            error_rate=error_rate,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            p50_response_time=sorted_times[p50_idx] if sorted_times else 0,
            p95_response_time=sorted_times[p95_idx] if sorted_times else 0,
            p99_response_time=sorted_times[p99_idx] if sorted_times else 0,
            throughput=total_requests / duration if duration > 0 else 0,
            duration=duration,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_after - memory_before,
            cpu_before=cpu_before,
            cpu_after=cpu_after,
            extra_metrics={
                'concurrent_users': concurrent_users,
                'errors': errors[:10]
            }
        )

    def run_stress_test(
        self,
        endpoint: Dict,
        start_users: int = 10,
        max_users: int = 200,
        step: int = 10,
        duration_per_step: int = 10
    ) -> List[BenchmarkResult]:
        """
        Stress test - gradually increase load until system fails
        """
        results = []
        prev_throughput = 0

        for users in range(start_users, max_users + 1, step):
            result = self.run_load_test(endpoint, users, duration_per_step)

            results.append(result)

            # Check if system is degrading (throughput dropped significantly)
            if prev_throughput > 0 and result.throughput < prev_throughput * 0.5:
                print(f"  System degradation detected at {users} users")
                break

            prev_throughput = result.throughput

            # Stop if error rate is too high
            if result.error_rate > 50:
                print(f"  High error rate ({result.error_rate:.1f}%) at {users} users - stopping")
                break

        return results

    def run_all_benchmarks(self, requests_per_endpoint: int = 20) -> List[BenchmarkResult]:
        """Run benchmarks on all configured endpoints"""
        results = []

        print("\n" + "="*60)
        print("API PERFORMANCE BENCHMARKING")
        print("="*60)

        for endpoint in self.endpoints:
            print(f"\nTesting: {endpoint['name']} ({endpoint['method']} {endpoint['path']})")
            result = self.measure_endpoint(endpoint, num_requests=requests_per_endpoint)
            results.append(result)
            print(result.summary())

        return results

    def _mock_result(self, name: str, users: int, duration: int) -> BenchmarkResult:
        """Return mock result when requests library is not available"""
        return BenchmarkResult(
            name=name,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            error_rate=100,
            avg_response_time=0,
            min_response_time=0,
            max_response_time=0,
            p50_response_time=0,
            p95_response_time=0,
            p99_response_time=0,
            throughput=0,
            duration=duration,
            extra_metrics={'error': 'requests library not available'}
        )


class FaceRecognitionBenchmark:
    """
    Performance benchmarks specifically for Face Recognition system
    """

    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.test_encodings = []
        self._generate_test_encodings()

    def _generate_test_encodings(self, count: int = 100):
        """Generate random face encodings for testing"""
        if not NUMPY_AVAILABLE:
            return

        # Standard face_recognition uses 128-dimensional vectors
        self.test_encodings = [
            np.random.rand(128).astype(np.float64) for _ in range(count)
        ]

    def benchmark_recognition(
        self,
        num_embeddings: int = 50,
        num_tests: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark face recognition with specified number of embeddings
        """
        if not NUMPY_AVAILABLE:
            return {'error': 'numpy not available'}

        # Use only needed test encodings
        test_set = self.test_encodings[:num_tests] if len(self.test_encodings) >= num_tests else []
        if not test_set:
            self._generate_test_encodings(num_tests)
            test_set = self.test_encodings[:num_tests]

        # Prepare known encodings (simulated)
        known_encodings = self.test_encodings[:num_embeddings]

        results = {
            'num_embeddings': num_embeddings,
            'num_tests': num_tests,
            'recognition_times': [],
            'total_time': 0
        }

        start_total = time.perf_counter()

        for test_encoding in test_set:
            start = time.perf_counter()

            # Simulate face distance calculation
            distances = []
            for known in known_encodings:
                dist = np.linalg.norm(test_encoding - known)
                distances.append(dist)

            elapsed = time.perf_counter() - start
            results['recognition_times'].append(elapsed)

        results['total_time'] = time.perf_counter() - start_total

        if results['recognition_times']:
            times = results['recognition_times']
            results.update({
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'p50_time': statistics.median(times),
                'p95_time': sorted(times)[int(len(times) * 0.95)],
                'throughput': num_tests / results['total_time']
            })

        return results

    def benchmark_recognition_with_scale(
        self,
        scales: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Benchmark recognition at different scales
        """
        if scales is None:
            scales = [10, 50, 100, 200, 500]

        print("\n" + "="*60)
        print("FACE RECOGNITION PERFORMANCE SCALING TEST")
        print("="*60)
        print(f"{'Embeddings':<12} {'Avg Time':<12} {'P95 Time':<12} {'Throughput':<15}")
        print("-"*60)

        results = []
        for scale in scales:
            result = self.benchmark_recognition(num_embeddings=scale, num_tests=50)
            results.append(result)

            print(
                f"{scale:<12} "
                f"{result.get('avg_time', 0)*1000:<10.2f}ms "
                f"{result.get('p95_time', 0)*1000:<10.2f}ms "
                f"{result.get('throughput', 0):<15.2f}"
            )

        return results

    def benchmark_cache_efficiency(
        self,
        num_requests: int = 100,
        cache_ttl: float = 10.0
    ) -> Dict[str, Any]:
        """
        Test cache efficiency by measuring repeated recognition calls
        """
        if not NUMPY_AVAILABLE:
            return {'error': 'numpy not available'}

        # Simulate cached vs non-cached scenarios
        test_encoding = self.test_encodings[0] if self.test_encodings else None
        if test_encoding is None:
            return {'error': 'No test encodings available'}

        results = {
            'num_requests': num_requests,
            'cache_ttl': cache_ttl,
            'times': [],
            'cache_hits': 0,
            'cache_misses': 0
        }

        # Simulate cache with TTL
        cache = {'data': None, 'timestamp': 0}

        for i in range(num_requests):
            start = time.perf_counter()

            # Check cache
            current_time = time.time()
            if cache['data'] is not None and (current_time - cache['timestamp']) < cache_ttl:
                results['cache_hits'] += 1
                # Use cached data (fast)
                known_encodings = cache['data']
            else:
                results['cache_misses'] += 1
                # Reload from "database" (slow)
                known_encodings = self.test_encodings[:50]
                cache['data'] = known_encodings
                cache['timestamp'] = current_time

            # Perform recognition
            distances = [np.linalg.norm(test_encoding - known) for known in known_encodings]

            elapsed = time.perf_counter() - start
            results['times'].append(elapsed)

        if results['times']:
            results['avg_time'] = statistics.mean(results['times'])
            results['hit_rate'] = results['cache_hits'] / num_requests * 100

        return results

    def measure_face_detection_speed(
        self,
        num_tests: int = 20
    ) -> Dict[str, Any]:
        """
        Measure face detection speed if face_recognition is available
        """
        try:
            import face_recognition
            has_face_recognition = True
        except ImportError:
            has_face_recognition = False

        if not has_face_recognition:
            return {'error': 'face_recognition library not available'}

        results = {
            'num_tests': num_tests,
            'detection_times': [],
            'encoding_times': []
        }

        # Create a dummy image (would normally be a real face image)
        dummy_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        for _ in range(num_tests):
            # Measure face detection
            start = time.perf_counter()
            face_locations = face_recognition.face_locations(dummy_image)
            detection_time = time.perf_counter() - start
            results['detection_times'].append(detection_time)

            # Measure encoding
            if face_locations:
                start = time.perf_counter()
                face_encodings = face_recognition.face_encodings(dummy_image, face_locations)
                encoding_time = time.perf_counter() - start
                results['encoding_times'].append(encoding_time)

        if results['detection_times']:
            results['avg_detection_time'] = statistics.mean(results['detection_times'])
            results['avg_encoding_time'] = statistics.mean(results['encoding_times']) if results['encoding_times'] else 0

        return results


class DatabaseQueryBenchmark:
    """
    Benchmark database query performance
    """

    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db

    def benchmark_query(
        self,
        query_name: str,
        query_func: callable,
        num_runs: int = 10
    ) -> Dict[str, Any]:
        """Benchmark a single query"""
        times = []
        errors = []

        for _ in range(num_runs):
            try:
                start = time.perf_counter()
                result = query_func()
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors.append(str(e))

        return {
            'query_name': query_name,
            'num_runs': num_runs,
            'num_errors': len(errors),
            'avg_time': statistics.mean(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'p95_time': sorted(times)[int(len(times) * 0.95)] if times else 0,
            'errors': errors[:5]
        }

    def benchmark_common_queries(self) -> List[Dict[str, Any]]:
        """Run benchmarks on common database queries"""
        if not self.app or not self.db:
            return [{'error': 'App and DB context required'}]

        results = []

        with self.app.app_context():
            # Query 1: Get all employees
            results.append(self.benchmark_query(
                'Get All Employees',
                lambda: self.db.session.query(self.db.Model.metadata.tables['employee']).all()
            ))

            # Query 2: Get today's attendance
            from datetime import date
            today = date.today()
            results.append(self.benchmark_query(
                'Get Today Attendance',
                lambda: self.db.session.query(
                    self.db.Model.metadata.tables['attendance']
                ).filter_by(date=today).all()
            ))

        return results


class ReportGenerator:
    """Generate performance test reports"""

    @staticmethod
    def generate_text_report(results: List[BenchmarkResult]) -> str:
        """Generate plain text report"""
        lines = [
            "="*70,
            "PERFORMANCE TEST REPORT",
            "="*70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        for result in results:
            lines.extend([
                "-"*70,
                result.name,
                "-"*70,
                f"  Total Requests:      {result.total_requests}",
                f"  Successful:          {result.successful_requests}",
                f"  Failed:              {result.failed_requests}",
                f"  Error Rate:          {result.error_rate:.2f}%",
                "",
                f"  Response Time:",
                f"    Average:           {result.avg_response_time*1000:.2f} ms",
                f"    Min:               {result.min_response_time*1000:.2f} ms",
                f"    Max:               {result.max_response_time*1000:.2f} ms",
                f"    P50:               {result.p50_response_time*1000:.2f} ms",
                f"    P95:               {result.p95_response_time*1000:.2f} ms",
                f"    P99:               {result.p99_response_time*1000:.2f} ms",
                "",
                f"  Throughput:          {result.throughput:.2f} requests/sec",
                f"  Duration:           {result.duration:.2f} sec",
                "",
            ])

            if result.memory_delta != 0:
                lines.append(f"  Memory Delta:        {result.memory_delta:.2f} MB")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_json_report(results: List[BenchmarkResult]) -> str:
        """Generate JSON report"""
        return json.dumps([r.to_dict() for r in results], indent=2)

    @staticmethod
    def save_report(results: List[BenchmarkResult], filepath: str, format: str = 'text'):
        """Save report to file"""
        if format == 'json':
            content = ReportGenerator.generate_json_report(results)
        else:
            content = ReportGenerator.generate_text_report(results)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Report saved to: {filepath}")


def run_quick_benchmark(base_url: str = 'http://localhost:5555') -> Dict[str, Any]:
    """
    Run a quick benchmark of all endpoints
    """
    benchmark = PerformanceBenchmark(base_url=base_url)
    results = benchmark.run_all_benchmarks(requests_per_endpoint=10)

    return {
        'results': [r.to_dict() for r in results],
        'summary': ReportGenerator.generate_text_report(results)
    }


if __name__ == '__main__':
    print("Performance Testing Module")
    print("="*50)
    print("\nUsage in Python:")
    print("  from tests.performance_test import PerformanceBenchmark")
    print("  benchmark = PerformanceBenchmark('http://localhost:5555')")
    print("  results = benchmark.run_all_benchmarks()")
    print("\nOr run benchmarks via: python tests/benchmark_runner.py")
