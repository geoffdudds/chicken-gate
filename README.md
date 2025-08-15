# Chicken Gate Control System

An automated chicken gate control system for Raspberry Pi with web interface.

## Features

- Automatic sunrise/sunset scheduling using astronomical calculations
- Manual gate control via web interface
- RESTful API for external control
- Email notifications for gate events
- Systemd service integration
- Robust error handling and recovery

## Project Structure

```
chicken-gate/
├── src/chicken_gate/           # Main package
│   ├── gate/                   # Gate control process
│   │   ├── main.py            # Main gate control loop
│   │   ├── gate.py            # Gate hardware interface
│   │   ├── schedule.py        # Sunrise/sunset scheduling
│   │   ├── gate_drv.py        # GPIO driver interface
│   │   ├── gate_cmd.py        # Command processing
│   │   ├── suntimes.py        # Sunrise/sunset calculations
│   │   └── email_me.py        # Email notification system
│   ├── web/                   # Web interface process
│   │   ├── app.py             # Flask web application
│   │   └── templates/         # HTML templates
│   └── shared/                # Shared modules
│       ├── config.py          # Configuration constants
│       ├── secret.toml.template # Email configuration template
│       └── timer.py           # Timing utilities
├── scripts/                   # Entry point scripts
│   ├── chicken-gate-main      # Gate process entry point
│   └── chicken-gate-web       # Web process entry point
├── systemd/                   # Systemd service files
│   ├── chicken-gate.service         # Gate control service
│   ├── chicken-gate-web.service     # Web interface service
│   └── chicken-gate-web-port80.service  # Web on port 80
├── test/                      # Unit tests
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_gate.py           # Core gate functionality tests
│   ├── test_gate_comprehensive.py  # Comprehensive gate tests
│   ├── test_gate_integration.py    # Integration tests with mock hardware
│   ├── test_timer.py          # Timer utility tests
│   └── test_utils.py          # Test utilities and helpers
└── pyproject.toml            # Modern Python packaging
```

## Installation

1. Clone the repository to your Raspberry Pi
2. Install in development mode:
   ```bash
   pip install -e .
   ```

This will automatically install all required dependencies with the correct versions as specified in `pyproject.toml`.

## Configuration

### Email Notifications

Configure email notifications using one of these methods:

**Method 1: Environment Variables (Recommended for Production)**

```bash
export CHICKEN_GATE_EMAIL_SENDER="your-email@gmail.com"
export CHICKEN_GATE_EMAIL_PASSWORD="your-app-password"  # Use Gmail App Password
export CHICKEN_GATE_EMAIL_RECIPIENT="recipient@gmail.com"
```

**Method 2: Configuration File (For Development)**

```bash
# Copy the template and edit with your values
cp src/chicken_gate/shared/secret.toml.template secret.toml
# Edit secret.toml with your actual credentials
```

**Gmail Setup:** Enable 2-factor authentication and generate an App Password at Google Account → Security → App passwords.

See `docs/configuration.md` for detailed setup instructions.

### Hardware Configuration

Edit the configuration in `src/chicken_gate/shared/config.py`:

- GPIO pin assignments
- Gate timing parameters
- API endpoints

## Running the Services

### Manual Testing

```bash
# Test gate control
chicken-gate-main

# Test web interface
chicken-gate-web
```

### Systemd Services

```bash
# Install services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable chicken-gate.service
sudo systemctl enable chicken-gate-web.service
sudo systemctl start chicken-gate.service
sudo systemctl start chicken-gate-web.service

# Check status
sudo systemctl status chicken-gate.service
sudo systemctl status chicken-gate-web.service
```

## Installation & Updates

Use the provided installation scripts:

```bash
# Install/Update gate service
./install-gate-service.sh

# Install/Update web service
./install-web-service.sh

# For production web service (port 80)
./install-web-service.sh --port80
```

These scripts will:

- Install systemd service files
- Stop any existing services
- Kill any manually running processes
- Enable and start the services
- Show status and helpful information

## API Endpoints

- `GET /api/status` - Get current gate status
- `POST /api/open` - Open the gate
- `POST /api/close` - Close the gate
- `POST /api/auto` - Enable automatic mode

## Utilities

Additional helper scripts:

```bash
# Send manual commands to gate
python send_gate_cmd.py OPEN
python send_gate_cmd.py CLOSE
python send_gate_cmd.py RESET
python send_gate_cmd.py RESET:50

# Direct systemctl commands
sudo systemctl start chicken-gate-web
sudo systemctl stop chicken-gate-web
sudo systemctl status chicken-gate

# System maintenance (when needed)
sudo apt update && sudo apt upgrade
pip install -e . --upgrade
```

## Development

Install development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest test/
```

Format code:

```bash
black src/ test/
```

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- Motor driver circuit for gate mechanism
- Limit switches for gate position detection
- Power supply for gate motor

## License

MIT License - see LICENSE file for details.
