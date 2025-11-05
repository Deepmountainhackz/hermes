# Hermes Tests

Test suite for the Hermes Intelligence Platform.

## Test Files

- test_country.py - Country data tests
- test_database.py - Database tests

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_country.py

# With coverage
python -m pytest tests/ --cov=services
```

## Writing Tests

Follow the existing patterns. Each test file should:
1. Import necessary modules
2. Set up test fixtures
3. Write clear, focused test cases
4. Clean up after tests
