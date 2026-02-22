# DevMetrics Test Suite

## Overview

Comprehensive test suite for the DevMetrics Dashboard collectors and storage layer.

## Test Structure

```
devmetrics/tests/
├── __init__.py
├── test_github_client.py          # GitHub API client tests
├── test_space_collector.py        # SPACE metrics collector tests
├── test_copilot_collector.py      # Copilot metrics collector tests
├── test_dummy_data_generator.py   # Dummy data generator tests
└── test_json_store.py             # JSON storage layer tests
```

## Test Coverage

### GitHubClient (`test_github_client.py`)
- ✅ Authentication with token and environment variables
- ✅ Rate limit detection and handling
- ✅ Rate limit retry logic
- ✅ Repository and organization retrieval
- ✅ Connection validation
- ✅ Error handling for invalid tokens
- ✅ Edge cases: empty tokens, past reset times

### SpaceCollector (`test_space_collector.py`)
- ✅ PR cycle time calculation
- ✅ Review turnaround time parsing
- ✅ Rework rate calculation
- ✅ WIP count collection
- ✅ Date range filtering
- ✅ Unmerged PR filtering
- ✅ Empty result handling
- ✅ Trend calculation (improving/stable/worsening)
- ✅ Multi-repo partial failure handling

### CopilotCollector (`test_copilot_collector.py`)
- ✅ Usage metrics parsing
- ✅ Acceptance rate calculation
- ✅ Seat utilization analysis
- ✅ Active vs inactive seat detection
- ✅ API error handling
- ✅ Missing enterprise/org configuration
- ✅ Zero suggestions/acceptances handling
- ✅ Trend detection for acceptance rates
- ✅ Missing fields in API responses

### DummyDataGenerator (`test_dummy_data_generator.py`)
- ✅ Deterministic data generation with seeds
- ✅ Data validation (ranges, formats, schemas)
- ✅ Schema compliance for all metrics
- ✅ PR cycle times generation
- ✅ Review turnaround generation
- ✅ Rework rates generation
- ✅ WIP counts generation
- ✅ Copilot usage metrics generation
- ✅ Acceptance rates generation
- ✅ Seat utilization generation
- ✅ Edge cases: empty repos, zero days history

### JSONStore (`test_json_store.py`)
- ✅ Read/write operations
- ✅ File initialization with metadata
- ✅ Data appending
- ✅ Date range queries
- ✅ Repository filtering
- ✅ Snapshot management (latest, list)
- ✅ Schema validation
- ✅ Statistics calculation
- ✅ Backup functionality
- ✅ Error handling: invalid JSON, missing files
- ✅ Edge cases: empty arrays, unicode, nested objects

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# From project root
pytest devmetrics/tests/ -v

# With coverage
pytest devmetrics/tests/ -v --cov=devmetrics --cov-report=html
```

### Run Specific Test Files

```bash
pytest devmetrics/tests/test_github_client.py -v
pytest devmetrics/tests/test_space_collector.py -v
pytest devmetrics/tests/test_copilot_collector.py -v
pytest devmetrics/tests/test_dummy_data_generator.py -v
pytest devmetrics/tests/test_json_store.py -v
```

### Run Specific Test Classes

```bash
pytest devmetrics/tests/test_github_client.py::TestGitHubClientRateLimit -v
pytest devmetrics/tests/test_space_collector.py::TestCollectPRCycleTimes -v
```

### Run with Different Verbosity

```bash
# Quiet (only test summary)
pytest devmetrics/tests/ -q

# Very verbose (show all test names)
pytest devmetrics/tests/ -vv

# Show print statements
pytest devmetrics/tests/ -v -s
```

## Test Configuration

Configuration is in `pytest.ini`:

```ini
[pytest]
testpaths = devmetrics/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Test Patterns

### Fixtures

Tests use pytest fixtures for setup:

```python
@pytest.fixture
def mock_client(self):
    """Create mock GitHub client."""
    # Setup code
    yield client
    # Teardown code
```

### Mocking

External dependencies are mocked:

```python
with patch('devmetrics.collectors.github_client.Github') as mock_github:
    # Test code
```

### Parameterization

Tests use parametrize for multiple scenarios:

```python
@pytest.mark.parametrize("rate,trend", [
    (0.5, "stable"),
    (0.7, "improving"),
    (0.3, "declining")
])
def test_trend_calculation(self, rate, trend):
    # Test code
```

## Edge Cases Tested

1. **Empty Data Sets**: All collectors handle empty results
2. **Missing Fields**: API responses with missing/null fields
3. **Rate Limiting**: GitHub rate limit detection and retry
4. **File I/O Errors**: Invalid JSON, missing files, permission errors
5. **Date Ranges**: Edge cases at boundaries, past/future dates
6. **Schema Validation**: Structure validation for all data types
7. **Zero Values**: Zero suggestions, acceptances, seats
8. **Unicode**: Proper handling of international characters

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

- No external API calls (all mocked)
- Deterministic results
- Fast execution (< 30 seconds for full suite)
- Isolated test cases (no shared state)

## Extending Tests

To add new tests:

1. Create test class: `class TestNewFeature:`
2. Add test methods: `def test_specific_behavior(self):`
3. Use fixtures for common setup
4. Mock external dependencies
5. Assert expected outcomes

Example:

```python
class TestNewCollector:
    @pytest.fixture
    def collector(self):
        return NewCollector(config={})
    
    def test_collect_data(self, collector):
        result = collector.collect()
        assert "data" in result
        assert len(result["data"]) > 0
```

## Known Issues

None currently. All tests passing with dummy data.

## Future Enhancements

- [ ] Integration tests with live GitHub API (optional)
- [ ] Performance benchmarks for large datasets
- [ ] Mutation testing for edge case coverage
- [ ] Property-based testing with Hypothesis
