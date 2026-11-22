"""
User-adjustable settings, shared by the gate and web services.

The web app validates and saves them to ``settings.json`` in the project root,
then tells the gate to reload. The file only changes when the user saves, so it
lives on the SD card and survives reboots.
"""

import json
import os
import re

from .config import get_settings_path

OPEN_EVENTS = ("dawn", "sunrise")
CLOSE_EVENTS = ("sunset", "dusk")

TRAVEL_RANGE = (30, 900)  # seconds
OFFSET_RANGE = (-120, 120)  # minutes

DEFAULTS = {
    "open_travel_s": 280,
    "close_travel_s": 420,
    "open_event": "sunrise",
    "open_offset_min": 0,
    "close_event": "dusk",
    "close_offset_min": 0,
}


def _int_in_range(data, key, bounds, label, unit):
    value = data.get(key, DEFAULTS[key])
    whole_float = isinstance(value, float) and value.is_integer()
    int_text = isinstance(value, str) and re.fullmatch(r"\s*[-+]?\d+\s*", value)
    if whole_float or int_text:
        value = int(value)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be a whole number")
    number = value
    low, high = bounds
    if not low <= number <= high:
        raise ValueError(f"{label} must be between {low} and {high} {unit}")
    return number


def _choice(data, key, choices, label):
    value = data.get(key, DEFAULTS[key])
    if value not in choices:
        raise ValueError(f"{label} must be one of: {', '.join(choices)}")
    return value


def validate(data):
    """Return a complete, validated copy of ``data``; raise ValueError if invalid.

    Missing keys take their default value; unknown keys are dropped.
    """
    if not isinstance(data, dict):
        raise ValueError("Settings must be an object")
    return {
        "open_travel_s": _int_in_range(
            data, "open_travel_s", TRAVEL_RANGE, "Lowering time", "seconds"
        ),
        "close_travel_s": _int_in_range(
            data, "close_travel_s", TRAVEL_RANGE, "Raising time", "seconds"
        ),
        "open_event": _choice(data, "open_event", OPEN_EVENTS, "Open event"),
        "open_offset_min": _int_in_range(
            data, "open_offset_min", OFFSET_RANGE, "Open offset", "minutes"
        ),
        "close_event": _choice(data, "close_event", CLOSE_EVENTS, "Close event"),
        "close_offset_min": _int_in_range(
            data, "close_offset_min", OFFSET_RANGE, "Close offset", "minutes"
        ),
    }


def load(path=None):
    """Load settings, falling back to defaults if the file is missing or bad."""
    path = path or get_settings_path()
    try:
        with open(path) as f:
            return validate(json.load(f))
    except FileNotFoundError:
        return dict(DEFAULTS)
    except (OSError, ValueError) as e:
        print(f"Ignoring invalid settings file {path}: {e}")
        return dict(DEFAULTS)


def save(data, path=None):
    """Validate and atomically write settings; return the saved values."""
    settings = validate(data)
    path = str(path or get_settings_path())
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return settings
