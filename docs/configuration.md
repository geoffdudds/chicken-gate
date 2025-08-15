# Configuration Setup Guide

This document explains how to configure secrets and credentials for the Chicken Gate project.

## Method 1: Environment Variables (Recommended for Production/CI)

Set these environment variables in your deployment environment:

```bash
# Email configuration
export CHICKEN_GATE_EMAIL_SENDER="your-email@gmail.com"
export CHICKEN_GATE_EMAIL_PASSWORD="your-app-password"  # Use Gmail App Password
export CHICKEN_GATE_EMAIL_RECIPIENT="recipient@gmail.com"
```

### For systemd services:

Add to your service file (`systemd/chicken-gate.service`):

```ini
[Service]
Environment=CHICKEN_GATE_EMAIL_SENDER=your-email@gmail.com
Environment=CHICKEN_GATE_EMAIL_PASSWORD=your-app-password
Environment=CHICKEN_GATE_EMAIL_RECIPIENT=recipient@gmail.com
```

### For CI/CD pipelines:

Set as GitHub Actions secrets, then in your workflow:

```yaml
env:
  CHICKEN_GATE_EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
  CHICKEN_GATE_EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
  CHICKEN_GATE_EMAIL_RECIPIENT: ${{ secrets.EMAIL_RECIPIENT }}
```

## Method 2: Local Configuration File

For local development or simple deployments:

1. Copy the template:

   ```bash
   cp src/chicken_gate/shared/secret.toml.template secret.toml
   ```

2. Edit `secret.toml` with your actual values:
   ```toml
   [secrets]
   sender = "your-email@gmail.com"
   password = "your-app-password"
   recipient = "recipient@gmail.com"
   ```

**Note:** The `secret.toml` file is git-ignored for security.

## Gmail App Password Setup

For Gmail, you need to:

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the App Password (not your regular password) in the configuration

## Testing Configuration

To test email configuration without sending actual emails, the system will validate the configuration on startup and provide helpful error messages if something is wrong.

## Priority

The system checks configuration in this order:

1. Environment variables (highest priority)
2. secret.toml file (fallback)
3. Error if neither is found
