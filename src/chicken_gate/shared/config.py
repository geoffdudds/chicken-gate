"""
Configuration settings for the chicken gate system.
"""

from pathlib import Path

# File paths for communication between processes
STATUS_FILE = "gate_status.json"
COMMAND_FILE = "gate_cmd.txt"

# Web interface settings
DEFAULT_WEB_PORT = 5000
PRODUCTION_WEB_PORT = 80

# Camera settings
CAMERA_IP = "192.168.0.135"
CAMERA_USERNAME = "chickencam"
CAMERA_PASSWORD = "password"

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Virtual environment path
VENV_PATH = PROJECT_ROOT / ".venv"


def get_status_file_path():
    """Get the full path to the status file."""
    return PROJECT_ROOT / STATUS_FILE


def get_command_file_path():
    """Get the full path to the command file."""
    return PROJECT_ROOT / COMMAND_FILE
