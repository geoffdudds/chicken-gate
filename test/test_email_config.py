"""
Test email configuration system
"""

import os
from unittest.mock import patch

import pytest
import toml

from chicken_gate.gate.email_me import get_email_config, send_email


class TestEmailConfiguration:
    """Test the email configuration system"""

    def test_environment_variables_priority(self):
        """Test that environment variables take priority over file"""
        with patch.dict(
            os.environ,
            {
                "CHICKEN_GATE_EMAIL_SENDER": "env@test.com",
                "CHICKEN_GATE_EMAIL_PASSWORD": "env_pass",
                "CHICKEN_GATE_EMAIL_RECIPIENT": "env_recipient@test.com",
            },
        ):
            sender, password, recipient = get_email_config()
            assert sender == "env@test.com"
            assert password == "env_pass"
            assert recipient == "env_recipient@test.com"

    def test_toml_file_fallback(self):
        """Test that TOML file is used when env vars not available"""
        # Clear any existing env vars
        with patch.dict(os.environ, {}, clear=True), patch(
            "pathlib.Path.exists", return_value=True
        ), patch(
            "toml.load",
            return_value={
                "secrets": {
                    "sender": "file@test.com",
                    "password": "file_pass",
                    "recipient": "file_recipient@test.com",
                }
            },
        ):
            sender, password, recipient = get_email_config()
            assert sender == "file@test.com"
            assert password == "file_pass"
            assert recipient == "file_recipient@test.com"

    def test_missing_configuration_error(self):
        """Test error when no configuration is available"""
        # Clear env vars and mock missing file
        with patch.dict(os.environ, {}, clear=True), patch(
            "pathlib.Path.exists", return_value=False
        ):
            with pytest.raises(ValueError) as exc_info:
                get_email_config()

            assert "Email configuration not found" in str(exc_info.value)

    def test_invalid_toml_file_error(self):
        """Test error when TOML file is invalid"""
        # Clear env vars
        with patch.dict(os.environ, {}, clear=True), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("toml.load", side_effect=toml.TomlDecodeError("Invalid TOML", "", 0)):
            with pytest.raises(ValueError) as exc_info:
                get_email_config()

            assert "Invalid secret.toml format" in str(exc_info.value)

    def test_send_email_success(self, mocker):
        """Test successful email sending"""
        # Set up environment
        with patch.dict(
            os.environ,
            {
                "CHICKEN_GATE_EMAIL_SENDER": "test@test.com",
                "CHICKEN_GATE_EMAIL_PASSWORD": "test_pass",
                "CHICKEN_GATE_EMAIL_RECIPIENT": "recipient@test.com",
            },
        ):
            # Mock successful SMTP
            mock_smtp = mocker.patch("chicken_gate.gate.email_me.smtplib.SMTP_SSL")
            mock_server = mock_smtp.return_value.__enter__.return_value

            result = send_email("Test message")

            assert result is True
            mock_server.login.assert_called_once_with("test@test.com", "test_pass")
            mock_server.sendmail.assert_called_once_with(
                "test@test.com",
                "recipient@test.com",
                "Subject: Chicken Gate Notification\n\nTest message",
            )

    def test_send_email_config_error(self):
        """Test email sending with config error"""
        # Clear env vars and mock missing file
        with patch.dict(os.environ, {}, clear=True), patch(
            "pathlib.Path.exists", return_value=False
        ):
            result = send_email("Test message")
            assert result is False

    def test_send_email_smtp_error(self, mocker):
        """Test email sending with SMTP error"""
        # Set up environment
        with patch.dict(
            os.environ,
            {
                "CHICKEN_GATE_EMAIL_SENDER": "test@test.com",
                "CHICKEN_GATE_EMAIL_PASSWORD": "test_pass",
                "CHICKEN_GATE_EMAIL_RECIPIENT": "recipient@test.com",
            },
        ):
            # Mock SMTP failure
            mock_smtp = mocker.patch("chicken_gate.gate.email_me.smtplib.SMTP_SSL")
            mock_smtp.side_effect = Exception("SMTP Error")

            result = send_email("Test message")
            assert result is False
