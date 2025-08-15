# Continuous Integration (CI/CD)

This project uses GitHub Actions for automated testing and quality assurance.

## Workflows

### `tests.yml` - Comprehensive Testing & Quality Assurance

- **Triggers**: Push to `master`/`main`, Pull Requests
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Tests**: Complete test suite with pytest (all tests including slow ones)
- **Linting**: Code formatting and linting with ruff, type checking with mypy
- **Security**: Vulnerability scanning (bandit, safety)
- **Caching**: Pip dependencies cached for faster builds
- **Artifacts**: Test results uploaded for debugging
- **Dependencies**: Uses `pyproject.toml[ci]` for clean dependency management (excludes RPi.GPIO)

## Environment Variables

The CI workflows automatically set these environment variables for testing:

```bash
TESTING=true
CHICKEN_GATE_EMAIL_SENDER=test@example.com
CHICKEN_GATE_EMAIL_PASSWORD=test_password
CHICKEN_GATE_EMAIL_RECIPIENT=test_recipient@example.com
```

## Dependencies Handling

- **RPi.GPIO**: Excluded from `[ci]` dependencies (not available on x86 CI runners)
- **pyproject.toml**: Uses `[ci]` optional dependencies for clean CI setup
- **Test Dependencies**: ruff, mypy, pytest installed via pyproject.toml
- **Editable Install**: Project installed in editable mode with `pip install -e .[ci]`

## Badges

The README displays live status badge showing:

- [![Tests](https://github.com/geoffdudds/chicken-gate/actions/workflows/tests.yml/badge.svg)](https://github.com/geoffdudds/chicken-gate/actions/workflows/tests.yml) - Complete test suite, linting, and security checks

## Local Testing

To run the same tests locally:

```bash
# Fast tests (excludes slow/integration tests)
python test_runner.py fast

# All tests (complete suite like CI)
python test_runner.py

# Ruff linting and formatting
ruff check src/ test/ --fix
ruff format src/ test/
```

# Direct pytest (CI equivalent)

pytest test/ -v --tb=short -m "not slow"

```

## Benefits

✅ **Automated Quality Assurance** - Every commit is tested
✅ **Multi-Python Support** - Ensures compatibility across versions
✅ **Fast Feedback** - Quick tests provide immediate results
✅ **Security Scanning** - Automated vulnerability detection
✅ **Code Quality** - Linting and formatting checks
✅ **Pull Request Protection** - Prevents breaking changes from merging
```
