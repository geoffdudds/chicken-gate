"""
Test email configuration functionality with proper pytest fixtures
"""
import pytest
from chicken_gate.gate.email_me import get_email_config


class TestEmailConfiguration:
    """Test the email configuration system using pytest fixtures"""

    def test_environment_variables_from_conftest(self):
        """Test that conftest.py sets up email environment variables"""
        # conftest.py should have set these automatically
        sender, password, recipient = get_email_config()
        assert sender == 'test@example.com'
        assert password == 'test_password'
        assert recipient == 'test_recipient@example.com'

    def test_environment_variables_are_set(self):
        """Test that conftest.py properly sets up the test environment"""
        import os

        # Check that the environment variables were set by conftest.py
        assert os.getenv('TESTING') == 'true'
        assert os.getenv('CHICKEN_GATE_EMAIL_SENDER') == 'test@example.com'
        assert os.getenv('CHICKEN_GATE_EMAIL_PASSWORD') == 'test_password'
        assert os.getenv('CHICKEN_GATE_EMAIL_RECIPIENT') == 'test_recipient@example.com'

    def test_mock_email_fixture_available(self, mock_email_send):
        """Test that the mock_email_send fixture is available and working"""
        from chicken_gate.gate.email_me import send_email

        # Call the mocked function
        result = send_email("Test message")

        # Check that it was mocked and called
        assert result is True
        mock_email_send.assert_called_once_with("Test message")
