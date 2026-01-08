# Nimbly Backend Tests

Comprehensive test suite for the Nimbly API backend.

## Test Structure

```
api/tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_auth.py             # Authentication tests
├── test_receipts.py         # Receipt upload and retrieval tests
├── test_parser.py           # Receipt parsing tests (enhanced)
├── test_insights.py         # Insight generation tests
├── test_integration.py      # End-to-end integration tests
├── test_properties.py       # Property-based tests (Hypothesis)
├── test_api_manual.py       # Manual API testing script
└── README.md                # This file
```

## Running Tests

### All Tests

```bash
# From project root
docker-compose exec api pytest

# With coverage
docker-compose exec api pytest --cov=api --cov-report=term-missing

# Verbose output
docker-compose exec api pytest -v
```

### Specific Test Files

```bash
# Authentication tests
docker-compose exec api pytest api/tests/test_auth.py

# Parser tests
docker-compose exec api pytest api/tests/test_parser.py

# Property-based tests
docker-compose exec api pytest api/tests/test_properties.py

# Integration tests
docker-compose exec api pytest api/tests/test_integration.py
```

### Specific Tests

```bash
# Single test function
docker-compose exec api pytest api/tests/test_auth.py::test_request_magic_link

# Tests matching pattern
docker-compose exec api pytest -k "auth"
```

### Using Scripts

```bash
# Automated test runner (from project root)
./scripts/test.sh        # Unix/Mac
scripts\test.bat         # Windows
```

## Test Categories

### Unit Tests

Test individual functions and components in isolation.

**Files:**
- `test_auth.py` - Authentication logic
- `test_parser.py` - Receipt parsing functions
- `test_receipts.py` - Receipt endpoints

**Example:**
```python
def test_normalize_store_name():
    assert normalize_store_name("Whole Foods Market") == "wholefoodsmarket"
    assert normalize_store_name("TRADER JOE'S") == "traderjoes"
```

### Integration Tests

Test complete workflows across multiple components.

**File:** `test_integration.py`

**Scenarios:**
- Complete authentication flow
- Receipt upload → parse → retrieve
- Multi-receipt insight generation
- User isolation and authorization

**Example:**
```python
def test_complete_receipt_workflow(client, auth_token):
    # Upload receipt
    response = client.post("/api/receipts/upload", ...)
    receipt_id = response.json()["id"]
    
    # Retrieve receipt
    response = client.get(f"/api/receipts/{receipt_id}", ...)
    assert response.status_code == 200
```

### Property-Based Tests

Use Hypothesis to test properties that should always hold true.

**File:** `test_properties.py`

**Properties tested:**
- Referential integrity (receipts belong to valid users)
- Round-trip properties (upload → retrieve consistency)
- Normalization consistency
- Insight generation thresholds
- Authorization enforcement

**Example:**
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_normalization_is_idempotent(text):
    """Normalizing twice should give same result"""
    once = normalize_product_name(text)
    twice = normalize_product_name(once)
    assert once == twice
```

### Manual Testing Scripts

For interactive testing and debugging.

**Files:**
- `test_api_manual.py` - Complete API workflow testing

**Run:**
```bash
conda run -n nimbly python api/tests/test_api_manual.py
```

## Test Fixtures

Defined in `conftest.py`:

### `client`
FastAPI test client for making requests.

```python
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
```

### `db`
Database session for direct database access.

```python
def test_create_user(db):
    user = User(email="test@example.com")
    db.add(user)
    db.commit()
```

### `test_user`
Pre-created test user.

```python
def test_user_receipts(client, test_user):
    # test_user is already in database
    assert test_user.email == "test@example.com"
```

### `auth_token`
Valid authentication token for protected endpoints.

```python
def test_protected_endpoint(client, auth_token):
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

### `sample_receipt_file`
Sample receipt file for upload testing.

```python
def test_upload_receipt(client, auth_token, sample_receipt_file):
    response = client.post(
        "/api/receipts/upload",
        files={"file": sample_receipt_file},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

## Writing New Tests

### 1. Choose Test Type

- **Unit test:** Testing a single function
- **Integration test:** Testing a complete workflow
- **Property test:** Testing invariants

### 2. Add to Appropriate File

```python
# api/tests/test_receipts.py

def test_receipt_upload_validation(client, auth_token):
    """Test that invalid file types are rejected"""
    # Arrange
    invalid_file = ("test.exe", b"invalid", "application/x-msdownload")
    
    # Act
    response = client.post(
        "/api/receipts/upload",
        files={"file": invalid_file},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
```

### 3. Follow Conventions

- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Use Arrange-Act-Assert pattern
- One assertion per test (when possible)
- Use fixtures for setup
- Clean up after tests (fixtures handle this)

### 4. Run and Verify

```bash
docker-compose exec api pytest api/tests/test_receipts.py::test_receipt_upload_validation -v
```

## Coverage

Check test coverage:

```bash
# Generate coverage report
docker-compose exec api pytest --cov=api --cov-report=html

# View report (generated in htmlcov/)
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

**Coverage goals:**
- Overall: >80%
- Critical paths (auth, parsing): >90%
- New features: 100%

## Continuous Integration

Tests run automatically on:
- Every push to main
- Every pull request
- Scheduled daily runs

All tests must pass before merging.

## Debugging Tests

### Verbose Output

```bash
docker-compose exec api pytest -v -s
```

### Stop on First Failure

```bash
docker-compose exec api pytest -x
```

### Run Last Failed Tests

```bash
docker-compose exec api pytest --lf
```

### Print Output

```bash
docker-compose exec api pytest -s  # Don't capture stdout
```

### Use Debugger

```python
def test_something(client):
    import pdb; pdb.set_trace()  # Breakpoint
    response = client.get("/api/endpoint")
```

## Common Issues

### Database State

Tests use a fresh database for each test. If you see state issues:

```bash
# Restart containers
docker-compose down
docker-compose up -d
```

### Import Errors

Make sure you're running tests from the container:

```bash
# ✓ Correct
docker-compose exec api pytest

# ✗ Wrong
pytest  # Running on host
```

### Fixture Not Found

Check `conftest.py` for available fixtures and ensure proper imports.

## Best Practices

1. **Keep tests fast** - Use mocks for external services
2. **Keep tests isolated** - Each test should be independent
3. **Keep tests readable** - Clear names and structure
4. **Keep tests maintainable** - DRY principle, use fixtures
5. **Test edge cases** - Not just happy paths
6. **Test error handling** - Verify proper error responses
7. **Update tests with code** - Tests are documentation

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
