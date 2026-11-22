"""
Configuration settings for the chicken gate system.
"""

from pathlib import Path

# File paths for communication between processes
STATUS_FILE = "chicken-gate-status.json"
COMMAND_FILE = "gate_cmd.txt"
SETTINGS_FILE = "settings.json"

# The status file is rewritten every second; keep it in RAM (tmpfs) when
# available so it doesn't wear out the Pi's SD card.
RAM_DIR = Path("/dev/shm")

# Restart detection (see gate/boot_check.py). The boot flag must be in RAM so
# it's cleared by a reboot; the clean-shutdown marker must survive one.
BOOT_FLAG_FILE = "chicken-gate-started"
CLEAN_SHUTDOWN_FILE = ".clean_shutdown"

# Web interface settings
DEFAULT_WEB_PORT = 5000
PRODUCTION_WEB_PORT = 80

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Virtual environment path
VENV_PATH = PROJECT_ROOT / ".venv"


def get_status_file_path():
    """Get the full path to the status file."""
    status_dir = RAM_DIR if RAM_DIR.is_dir() else PROJECT_ROOT
    return status_dir / STATUS_FILE


def get_boot_flag_path():
    """Get the path of the flag marking that the gate has started this boot."""
    flag_dir = RAM_DIR if RAM_DIR.is_dir() else PROJECT_ROOT
    return flag_dir / BOOT_FLAG_FILE


def get_clean_shutdown_path():
    """Get the path of the marker written when the gate process stops cleanly."""
    return PROJECT_ROOT / CLEAN_SHUTDOWN_FILE


def get_settings_path():
    """Get the path of the user settings file (see shared/settings.py)."""
    return PROJECT_ROOT / SETTINGS_FILE


def get_command_file_path():
    """Get the full path to the command file."""
    return PROJECT_ROOT / COMMAND_FILE
