import os
import smtplib
import ssl
from pathlib import Path

import toml


def get_email_config():
    """Get email configuration from environment variables or secret.toml file"""
    # Try environment variables first (recommended for production)
    sender = os.getenv("CHICKEN_GATE_EMAIL_SENDER")
    password = os.getenv("CHICKEN_GATE_EMAIL_PASSWORD")
    recipient = os.getenv("CHICKEN_GATE_EMAIL_RECIPIENT")

    if sender and password and recipient:
        return sender, password, recipient

    # Fallback to secret.toml file - check multiple locations
    current_dir = Path.cwd()
    possible_locations = [
        current_dir / "secret.toml",  # Current working directory
        current_dir
        / "src"
        / "chicken_gate"
        / "shared"
        / "secret.toml",  # From project root
        Path(__file__).parent.parent
        / "shared"
        / "secret.toml",  # Relative to this module
    ]

    secret_file = None
    for location in possible_locations:
        if location.exists():
            secret_file = location
            break

    if secret_file:
        try:
            secret = toml.load(secret_file)
            return (
                secret["secrets"]["sender"],
                secret["secrets"]["password"],
                secret["secrets"]["recipient"],
            )
        except (KeyError, toml.TomlDecodeError) as e:
            raise ValueError(f"Invalid secret.toml format: {e}")

    # If neither works, provide helpful error with template location
    template_location = Path(__file__).parent.parent / "shared" / "secret.toml.template"
    raise ValueError(
        "Email configuration not found. Either:\n"
        "1. Set environment variables: CHICKEN_GATE_EMAIL_SENDER, CHICKEN_GATE_EMAIL_PASSWORD, CHICKEN_GATE_EMAIL_RECIPIENT\n"
        f"2. Create secret.toml file (copy from {template_location})"
    )


def send_email(msg):
    """Send email notification"""
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    try:
        sender_email, password, receiver_email = get_email_config()
    except ValueError as e:
        print(f"Email configuration error: {e}")
        return False

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
