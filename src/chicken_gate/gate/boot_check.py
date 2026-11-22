"""Detect restarts that weren't preceded by a clean shutdown.

A clean stop (reboot, shutdown or service restart) leaves a marker file on the
SD card. If the first gate start after a boot finds no marker, the Pi went down
without stopping cleanly: a hardware watchdog reset after a hang, or power loss.
"""

import contextlib
import os
import threading
import time
from pathlib import Path

from ..shared import config
from . import email_me

# Only a start this soon after boot counts as "the Pi restarted"; this also
# keeps the first deploy of this check from reporting a restart.
MAX_UPTIME_FOR_BOOT_S = 600
EMAIL_ATTEMPTS = 10
EMAIL_RETRY_DELAY_S = 60  # Wi-Fi can take a while to come up after boot
LOG_FILES = (Path("/var/log/syslog.1"), Path("/var/log/syslog"))
MAX_LOG_BYTES = 256 * 1024
MAX_LOG_LINES = 20
MAX_LOG_LINE_LENGTH = 300


def _uptime_s():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


def check_for_unexpected_restart(uptime_s=None):
    """Call once at startup. Returns True if the Pi restarted without a clean shutdown."""
    if uptime_s is None:
        uptime_s = _uptime_s()

    # The boot flag lives in RAM, so it only exists if the gate already started this boot
    boot_flag = config.get_boot_flag_path()
    first_start_this_boot = not boot_flag.exists()
    boot_flag.touch()

    clean_marker = config.get_clean_shutdown_path()
    was_clean = clean_marker.exists()
    with contextlib.suppress(FileNotFoundError):
        clean_marker.unlink()

    return first_start_this_boot and uptime_s < MAX_UPTIME_FOR_BOOT_S and not was_clean


def record_clean_shutdown():
    """Call when the gate process stops normally."""
    with open(config.get_clean_shutdown_path(), "w") as f:
        f.flush()
        os.fsync(f.fileno())


def get_previous_boot_log_summary(log_files=None):
    """Return a short syslog excerpt from before the current boot."""
    if log_files is None:
        log_files = LOG_FILES

    log_lines = []
    read_errors = []
    for path in log_files:
        try:
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(max(0, size - MAX_LOG_BYTES))
                data = f.read()
        except FileNotFoundError:
            continue
        except OSError as e:
            read_errors.append(f"{path}: {e}")
            continue

        if size > MAX_LOG_BYTES:
            data = data.split(b"\n", 1)[-1]
        log_lines.extend(data.decode("utf-8", "replace").splitlines())

    # Syslog timestamps can be wrong before NTP sync, so use file order.
    boot_marker = -1
    gate_start = -1
    for index, line in enumerate(log_lines):
        if "Starting System Logging Service" in line or (
            "rsyslogd:" in line and line.endswith(" start")
        ):
            boot_marker = index

    if boot_marker >= 0:
        for index, line in enumerate(log_lines[:boot_marker]):
            if "Started chicken gate" in line:
                gate_start = index
        start = (
            gate_start + 1
            if gate_start >= 0
            else max(0, boot_marker - MAX_LOG_LINES)
        )
        previous_boot_lines = log_lines[start:boot_marker]
        if previous_boot_lines:
            return "\n".join(
                line[:MAX_LOG_LINE_LENGTH]
                for line in previous_boot_lines[-MAX_LOG_LINES:]
            )
    if read_errors:
        return "Could not read persistent system logs: " + "; ".join(read_errors)
    return "No previous-boot entries found in the persistent system logs."


def notify_unexpected_restart(closed_switch_pressed):
    """Email about the restart in the background, retrying until the network is up."""
    position = "closed (closed switch pressed)" if closed_switch_pressed else "open"
    body = (
        "The chicken gate Pi restarted without a clean shutdown. This is most "
        "likely the hardware watchdog resetting a hung system, or a power loss.\n\n"
        f"The gate position was reset from the closed switch and is assumed {position}."
        "\n\nMost recent system log entries before this boot:\n"
        f"{get_previous_boot_log_summary()}"
    )

    def send():
        for _ in range(EMAIL_ATTEMPTS):
            if email_me.send_email(body, subject="Chicken gate restarted unexpectedly"):
                return
            time.sleep(EMAIL_RETRY_DELAY_S)

    threading.Thread(target=send, daemon=True).start()
