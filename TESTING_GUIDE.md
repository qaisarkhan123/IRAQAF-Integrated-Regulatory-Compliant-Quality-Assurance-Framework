# Testing Guide - Regulatory Monitoring Module

## Quick Start

### 1. Install Test Dependencies

```bash
# Install testing packages
pip install -r tests/requirements-test.txt

# Or install individually
pip install pytest pytest-cov pytest-mock pytest-xdist
```

### 2. Run Tests

```bash
# Run all tests
python tests/run_tests.py --all

# Run specific category
python tests/run_tests.py --unit          # Unit tests only
python tests/run_tests.py --integration   # Integration tests only
python tests/run_tests.py --e2e          # E2E tests only
python tests/run_tests.py --performance   # Performance tests only

# Run with coverage
python tests/run_tests.py --coverage
```

### 3. Manual Test Execution

```bash
# Using pytest directly
cd tests

# Run all tests
pytest -v

# Run specific file
pytest test_regulatory_monitor.py -v

# Run specific test
pytest test_regulatory_monitor.py::TestRegulatoryMonitor::test_cache_save_and_load -v

# Run with markers
pytest -m "unit" -v

# Run with coverage
pytest --cov=../scripts --cov-report=html
```

---

## Test Organization

```
tests/
├── test_regulatory_monitor.py      (Unit tests - 10 tests)
├── test_nlp_change_detector.py     (Unit tests - 20 tests)
├── test_integration.py              (Integration tests - 10 tests)
├── test_e2e.py                      (E2E tests - 8 tests)
├── test_performance.py              (Performance tests - 7 tests)
├── run_tests.py                     (Test runner)
├── requirements-test.txt            (Test dependencies)
└── conftest.py                      (Shared fixtures - optional)
```

---

## Test Categories

### Unit Tests (40 tests)

**File**: `test_regulatory_monitor.py`, `test_nlp_change_detector.py`

**Tests individual components**:
- Regulatory Monitor: Cache operations, data validation, versioning
- NLP Detector: Similarity calculation, severity classification, clause extraction

**Run**:
```bash
python tests/run_tests.py --unit
pytest tests/test_*regulatory_monitor.py tests/test_nlp_change_detector.py -v
```

### Integration Tests (10 tests)

**File**: `test_integration.py`

**Tests module interactions**:
- Fetch → Analyze → Detect workflow
- Data consistency across modules
- Error propagation
- State management
- Cache consistency

**Run**:
```bash
python tests/run_tests.py --integration
pytest tests/test_integration.py -v
```

### E2E Tests (8 tests)

**File**: `test_e2e.py`

**Tests complete workflows**:
- Complete monitoring cycle
- Multi-cycle tracking
- Data persistence
- Error recovery
- Report generation
- Large dataset processing

**Run**:
```bash
python tests/run_tests.py --e2e
pytest tests/test_e2e.py -v
```

### Performance Tests (7 tests)

**File**: `test_performance.py`

**Tests performance metrics**:
- Single calculation speed
- Batch processing (30 items)
- Large text handling
- 100+ regulation processing
- Concurrent operations
- Memory efficiency
- Scalability

**Run**:
```bash
python tests/run_tests.py --performance
pytest tests/test_performance.py -v -s
```

---

## Test Execution Workflows

### Quick Verification (2 minutes)

```bash
# Run only critical unit tests
pytest tests/test_regulatory_monitor.py::TestRegulatoryMonitor::test_cache_save_and_load -v
pytest tests/test_nlp_change_detector.py::TestNLPChangeDetector::test_similarity_identical_texts -v
```

### Development Cycle (5 minutes)

```bash
# Run all unit tests with minimal output
pytest tests/ -k "unit" --tb=short -q
```

### Pre-Commit (10 minutes)

```bash
# Run unit + integration tests
pytest tests/test_unit_*.py tests/test_integration.py -v --tb=short
```

### Full Verification (30 minutes)

```bash
# Run all tests with coverage
pytest tests/ -v --cov=../scripts --cov-report=html --cov-report=term
```

### Performance Baseline (15 minutes)

```bash
# Run performance tests with output
pytest tests/test_performance.py -v -s
```

---

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### View Coverage in Terminal

```bash
pytest tests/ --cov=scripts --cov-report=term-missing
```

### Coverage Targets

| Component | Target | Actual |
|-----------|--------|--------|
| regulatory_monitor.py | 90% | TBD |
| nlp_change_detector.py | 90% | TBD |
| iraqaf_regulatory_sync.py | 85% | TBD |
| Overall | 85% | TBD |

---

## Test Results Interpretation

### Success Output

```
tests/test_regulatory_monitor.py::TestRegulatoryMonitor::test_cache_save_and_load PASSED
tests/test_nlp_change_detector.py::TestNLPChangeDetector::test_similarity_identical_texts PASSED
...
================ 65 passed in 12.34s ================
```

### Failure Output

```
FAILED tests/test_regulatory_monitor.py::TestRegulatoryMonitor::test_cache_save_and_load
AssertionError: assert 'test' == 'production'

Expected 'production', but got 'test'

tests/test_nlp_change_detector.py::TestNLPChangeDetector::test_similarity_identical_texts PASSED
...
================ 1 failed, 64 passed in 15.23s ================
```

### Performance Metrics

```
Batch 30 calculations: 2.345s (0.078s per item)
100 regulations: 4.567s (0.046s per regulation)
Concurrent (10 threads): 1.234s
```

---

## Common Test Commands

| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | Run all tests with verbose output |
| `pytest tests/ -q` | Run all tests with minimal output |
| `pytest tests/ -x` | Stop at first failure |
| `pytest tests/ -k "similarity"` | Run tests matching pattern |
| `pytest tests/test_*.py --tb=short` | Run with short traceback |
| `pytest tests/ --lf` | Run last failed tests |
| `pytest tests/ -n auto` | Run in parallel (requires pytest-xdist) |
| `pytest tests/ --maxfail=3` | Stop after 3 failures |
| `pytest tests/ --durations=10` | Show 10 slowest tests |

---

## Troubleshooting

### Tests Can't Find Modules

**Problem**: `ImportError: cannot import name 'RegulatoryMonitor'`

**Solution**:
```bash
# Ensure PYTHONPATH includes scripts directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
pytest tests/ -v
```

### Pytest Not Found

**Problem**: `pytest: command not found`

**Solution**:
```bash
pip install -r tests/requirements-test.txt
python -m pytest tests/ -v
```

### Tests Timeout

**Problem**: Tests hang or timeout

**Solution**:
```bash
# Add timeout
pytest tests/ --timeout=10 -v
```

### Performance Tests Too Slow

**Problem**: Performance tests take too long

**Solution**:
```bash
# Skip performance tests
pytest tests/ -k "not performance" -v

# Or run only quick performance tests
pytest tests/test_performance.py::TestPerformance::test_single_similarity_calculation_speed -v
```

---

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r tests/requirements-test.txt
      - run: pytest tests/ --cov=scripts
      - uses: codecov/codecov-action@v3
```

### Local CI Simulation

```bash
# Run all tests as CI would
python -m pytest tests/ \
  -v \
  --cov=scripts \
  --cov-report=xml \
  --cov-report=term \
  --tb=short \
  --maxfail=1
```

---

## Test Development

### Creating New Tests

1. **Create test file**: `test_new_module.py`

```python
import pytest

class TestNewModule:
    @pytest.fixture
    def module(self):
        from new_module import NewModule
        return NewModule()
    
    def test_functionality(self, module):
        result = module.do_something()
        assert result == expected_value
```

2. **Add to appropriate category**:
   - Unit: `test_unit_new.py`
   - Integration: `test_integration_new.py`
   - E2E: `test_e2e_new.py`

3. **Run tests**:
```bash
pytest tests/test_unit_new.py -v
```

### Test Naming Convention

```python
# ✓ Good
def test_cache_save_and_load():
def test_similarity_identical_texts_high_similarity():
def test_monitor_invalid_data_raises_error():

# ✗ Bad
def test1():
def cache_test():
def testCacheSaveAndLoad():
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Tests** | 65+ |
| **Unit Tests** | 40 tests |
| **Integration Tests** | 10 tests |
| **E2E Tests** | 8 tests |
| **Performance Tests** | 7 tests |
| **Coverage Target** | 85%+ |
| **Execution Time** | < 2 minutes (all tests) |
| **Framework** | pytest |

---

## Next Steps

1. ✅ Install test dependencies
2. ✅ Run quick unit tests
3. ✅ Generate coverage report
4. ✅ Integrate into CI/CD
5. ✅ Monitor test trends

For questions or issues, check test logs and documentation.
