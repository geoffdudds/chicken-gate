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
│       └── timer.py           # Timing utilities
├── scripts/                   # Entry point scripts
│   ├── chicken-gate-main      # Gate process entry point
│   └── chicken-gate-web       # Web process entry point
├── systemd/                   # Systemd service files
│   ├── chicken-gate.service         # Gate control service
│   ├── chicken-gate-web.service     # Web interface service
│   └── chicken-gate-web-port80.service  # Web on port 80
├── test/                      # Unit tests
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

Edit the configuration in `src/chicken_gate/shared/config.py`:

- GPIO pin assignments
- Gate timing parameters
- Email settings
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
