# Contributing to Hermes Intelligence Platform

Thank you for your interest in contributing to Hermes! This document provides guidelines and best practices for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Commit Messages](#commit-messages)
7. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a positive environment

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Gather detailed information

Bug reports should include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or logs
- Screenshots if applicable

### Suggesting Features

Feature suggestions should include:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach
- Any alternative solutions considered

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- API keys (Alpha Vantage, NASA, OpenWeatherMap)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/hermes.git
cd hermes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests pandas python-dotenv feedparser streamlit plotly

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python database/setup_database.py

# Test a collector
python services/markets/fetch_market_data.py
```

---

## Coding Standards

### Python Style

Follow PEP 8 guidelines:

```python
# Good
def fetch_stock_data(symbol: str, api_key: str) -> dict:
    """
    Fetch stock data from Alpha Vantage API.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        api_key: Alpha Vantage API key
        
    Returns:
        Dictionary containing stock data
    """
    pass

# Bad
def fetchStockData(symbol,api_key):
    pass
```

### Naming Conventions

- **Files:** `snake_case.py`
- **Functions:** `snake_case()`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_CASE`
- **Variables:** `snake_case`

### Documentation

- Add docstrings to all functions and classes
- Use type hints where appropriate
- Comment complex logic
- Keep comments up-to-date

Example:

```python
def save_to_database(data: list[dict]) -> int:
    """
    Save collected data to the database.
    
    Args:
        data: List of dictionaries containing the data to save
        
    Returns:
        Number of records successfully saved
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    pass
```

### Error Handling

Always handle potential errors:

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return None
```

### Database Operations

- Always close connections
- Use context managers when possible
- Handle IntegrityError for duplicates

```python
conn = connect_db()
try:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
    conn.commit()
except sqlite3.IntegrityError:
    print("Duplicate record, skipping")
finally:
    conn.close()
```

---

## Testing Guidelines

### Before Submitting

1. **Test your collector:**
   ```bash
   python services/your_layer/your_collector.py
   ```

2. **Verify database integration:**
   ```bash
   python query_hermes.py
   ```

3. **Check dashboard compatibility:**
   ```bash
   streamlit run hermes_dashboard.py
   ```

4. **Test automation compatibility:**
   - Ensure no interactive prompts in automation
   - Use `sys.stdin.isatty()` for detection

### Manual Testing Checklist

- [ ] Collector runs without errors
- [ ] Data saves to database correctly
- [ ] Duplicate prevention works
- [ ] Error handling works for API failures
- [ ] Dashboard displays new data
- [ ] No interactive prompts in non-TTY mode

---

## Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(space): Add satellite tracking collector

Add new collector for tracking satellites using N2YO API.
Includes database schema updates and dashboard integration.

Closes #42
```

```
fix(weather): Handle missing wind_direction field

Some weather API responses don't include wind direction.
Updated collector to handle this gracefully with default value.
```

```
docs: Update README with PostgreSQL migration guide

Added step-by-step instructions for migrating from SQLite
to PostgreSQL for production deployments.
```

---

## Pull Request Process

### Before Submitting

1. Update documentation if needed
2. Add your changes to CHANGELOG.md
3. Test thoroughly (see Testing Guidelines)
4. Ensure code follows style guidelines
5. Rebase on latest main branch

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

## Related Issues
Closes #(issue number)
```

### Review Process

1. Automated checks must pass
2. At least one approval required
3. Address all review comments
4. Keep discussion focused and professional

---

## Project Structure

```
hermes/
├── .github/workflows/     # GitHub Actions
├── database/              # Database setup
├── services/              # Data collectors
│   ├── markets/
│   ├── space/
│   ├── environment/
│   └── social/
├── hermes.db              # SQLite database
├── run_hermes.py          # Master control
├── query_hermes.py        # Query tool
├── hermes_dashboard.py    # Web dashboard
└── README.md              # Documentation
```

### Adding a New Collector

1. Create file in appropriate `services/` subdirectory
2. Follow existing collector structure
3. Add database table in `database/setup_database.py`
4. Update `run_hermes.py` to include new collector
5. Add dashboard visualization
6. Update README.md
7. Test thoroughly

---

## Adding a New Data Source

### Checklist

- [ ] Research API (rate limits, authentication, etc.)
- [ ] Get API key/credentials
- [ ] Design database table
- [ ] Create collector script
- [ ] Test data collection
- [ ] Add to automation workflow
- [ ] Update dashboard
- [ ] Document in README

---

## Questions?

If you have questions:
1. Check existing documentation
2. Search closed issues
3. Open a new discussion
4. Ask in pull request comments

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- README.md (Contributors section)
- Release notes

---

**Thank you for contributing to Hermes! 🚀**
