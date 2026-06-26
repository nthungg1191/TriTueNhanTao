# Performance Testing Suite

Bộ công cụ kiểm thử hiệu năng toàn diện cho hệ thống quản lý chấm công.

## Cau truc

```
tests/
├── performance_test.py      # Core benchmarking module
├── benchmark_runner.py      # CLI runner
└── __init__.py
```

## Tinh nang

### 1. API Benchmarking
- Do thoi gian phan hoi cac endpoints
- Tinh toan percentile (p50, p95, p99)
- Do throughput (requests/second)

### 2. Load Testing
- Gia lap nhieu concurrent users
- Danh gia hieu nang khi co nhieu nguoi dung dong thoi

### 3. Stress Testing
- Tang dan so luong users cho den khi he thong chiu tai toi da
- Xac dinh bottleneck

### 4. Face Recognition Performance
- Do toc do nhan dien khuon mat voi cac muc scale khac nhau
- Danh gia hieu qua cache

## Cu phap su dung

### Chay tat ca benchmarks

```bash
python tests/benchmark_runner.py --all
```

### API Benchmarks

```bash
# Benchmark mac dinh (20 requests/endpoint)
python tests/benchmark_runner.py --api

# Tuychinh so request
python tests/benchmark_runner.py --api --requests 50

# Tuychinh base URL
python tests/benchmark_runner.py --api --base-url http://localhost:5000
```

### Load Testing

```bash
# Load test voi 100 concurrent users trong 30s
python tests/benchmark_runner.py --load --users 100 --duration 30

# Load test voi 200 users trong 60s
python tests/benchmark_runner.py --load --users 200 --duration 60
```

### Stress Testing

```bash
# Bat dau tu 10 users, toi da 200 users, tang 10 moi lan
python tests/benchmark_runner.py --stress

# Tuy chinh tham so
python tests/benchmark_runner.py --stress --start-users 5 --max-users 500 --step 25
```

### Face Recognition Benchmarks

```bash
# Tat ca face recognition tests
python tests/benchmark_runner.py --face

# Chi test voi cac scale cu the
python tests/benchmark_runner.py --face --face-scale 10,50,100,200

# Chi test cache efficiency
python tests/benchmark_runner.py --face --face-cache

# Chi test face detection speed
python tests/benchmark_runner.py --face --face-detection
```

### Database Benchmarks

```bash
python tests/benchmark_runner.py --db
```

### Xuat bao cao

```bash
# Xuat JSON
python tests/benchmark_runner.py --all --report json --output results.json

# Xuat text (mac dinh)
python tests/benchmark_runner.py --all --output results.txt
```

## Su dung trong Python

```python
from tests.performance_test import PerformanceBenchmark, FaceRecognitionBenchmark

# API Benchmark
benchmark = PerformanceBenchmark(base_url='http://localhost:5555')
results = benchmark.run_all_benchmarks(requests_per_endpoint=20)

# Face Recognition Benchmark
face_benchmark = FaceRecognitionBenchmark()
results = face_benchmark.benchmark_recognition_with_scale(scales=[10, 50, 100])

# Load Test
result = benchmark.run_load_test(endpoint, concurrent_users=100, duration_seconds=30)

# Stress Test
results = benchmark.run_stress_test(endpoint, start_users=10, max_users=200)
```

## Metrics

Cac metrics duoc thu thap:

| Metric | Mo ta |
|--------|-------|
| `avg_response_time` | Thoi gian phan hoi trung binh (ms) |
| `p50_response_time` | Median response time (ms) |
| `p95_response_time` | 95th percentile response time (ms) |
| `p99_response_time` | 99th percentile response time (ms) |
| `throughput` | So request moi giay |
| `error_rate` | Ty le loi (%) |
| `memory_delta` | Buoc tieu thu bo nho (MB) |

## Dependencies

Cac thu vien can thiet (da them vao requirements.txt):

- `psutil` - Theo doi tai nguyen he thong
- `requests` - HTTP requests cho API testing
- `numpy` - Xu ly ma tran (cho face recognition)
- `face-recognition` - Thu vien nhan dien khuon mat

## Luru y

1. **Server phai dang chay** khi test API endpoints
2. **Face recognition tests** se tao dummy encodings neu khong co du lieu thuc
3. **Database benchmarks** yeu cau server va database phai accessible

## Vi du ket qua

```
======================================================================
  API BENCHMARK SUMMARY
======================================================================

List Employees:
  Avg: 45.23ms | P95: 89.12ms | Throughput: 221.45 req/s

Today Attendance:
  Avg: 32.15ms | P95: 67.89ms | Throughput: 311.02 req/s

System Stats:
  Avg: 28.45ms | P95: 55.67ms | Throughput: 351.56 req/s
```
