"""
Pytest configuration and shared fixtures for chicken gate tests.
This file is automatically discovered by pytest and provides shared test setup.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

# Add src to Python path for testing
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-scoped fixture that sets up the test environment.
    Runs once at the beginning of the test session.
    """
    # Set testing flag
    os.environ['TESTING'] = 'true'

    # Set up test email configuration to prevent config errors
    original_env = {}
    test_email_vars = {
        'CHICKEN_GATE_EMAIL_SENDER': 'test@example.com',
        'CHICKEN_GATE_EMAIL_PASSWORD': 'test_password',
        'CHICKEN_GATE_EMAIL_RECIPIENT': 'test_recipient@example.com'
    }

    # Store original values and set test values
    for key, value in test_email_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield  # Run all tests

    # Cleanup: restore original environment
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_email_send():
    """
    Fixture to mock email sending in tests.
    Use this when you want to test email functionality without actually sending emails.
    """
    with patch('chicken_gate.gate.email_me.send_email', return_value=True) as mock:
        yield mock


@pytest.fixture(autouse=True)
def auto_mock_email():
    """
    Automatically mock email sending for all tests to prevent actual email sending.
    This runs for every test unless explicitly disabled.
    """
    with patch('chicken_gate.gate.email_me.send_email', return_value=True):
        yield


@pytest.fixture
def mock_rpi_gpio():
    """
    Fixture to mock RPi.GPIO for testing on non-Pi systems.
    """
    with patch.dict('sys.modules', {'RPi': object(), 'RPi.GPIO': object()}):
        # Import and patch after modules are in sys.modules
        from unittest.mock import Mock

        mock_gpio = Mock()
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.OUT = 0
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        mock_gpio.PUD_UP = 22

        # Mock methods
        mock_gpio.setmode = Mock()
        mock_gpio.setwarnings = Mock()
        mock_gpio.setup = Mock()
        mock_gpio.input = Mock(return_value=0)  # Default to LOW
        mock_gpio.output = Mock()
        mock_gpio.cleanup = Mock()

        with patch('RPi.GPIO', mock_gpio):
            yield mock_gpio


@pytest.fixture
def clean_environment():
    """
    Fixture that provides a clean environment for tests that need to test
    configuration loading without interference from test setup.
    """
    # Store current environment
    original_env = dict(os.environ)

    # Clear test email vars to test config loading
    test_vars = ['CHICKEN_GATE_EMAIL_SENDER', 'CHICKEN_GATE_EMAIL_PASSWORD', 'CHICKEN_GATE_EMAIL_RECIPIENT']
    for var in test_vars:
        os.environ.pop(var, None)

    yield

    # Restore environment
    os.environ.clear()
    os.environ.update(original_env)


# Pytest markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (may take several seconds)")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "hardware: marks tests that require actual hardware")
