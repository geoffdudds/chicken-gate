"""Detect restarts that weren't preceded by a clean shutdown.

A clean stop (reboot, shutdown or service restart) leaves a marker file on the
SD card. If the first gate start after a boot finds no marker, the Pi went down
without stopping cleanly: a hardware watchdog reset after a hang, or power loss.
"""

import contextlib
import os
import threading
import time

from ..shared import config
from . import email_me

# Only a start this soon after boot counts as "the Pi restarted"; this also
# keeps the first deploy of this check from reporting a restart.
MAX_UPTIME_FOR_BOOT_S = 600
EMAIL_ATTEMPTS = 10
EMAIL_RETRY_DELAY_S = 60  # Wi-Fi can take a while to come up after boot


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


def notify_unexpected_restart(closed_switch_pressed):
    """Email about the restart in the background, retrying until the network is up."""
    position = "closed (closed switch pressed)" if closed_switch_pressed else "open"
    body = (
        "The chicken gate Pi restarted without a clean shutdown. This is most "
        "likely the hardware watchdog resetting a hung system, or a power loss.\n\n"
        f"The gate position was reset from the closed switch and is assumed {position}."
    )

    def send():
        for _ in range(EMAIL_ATTEMPTS):
            if email_me.send_email(body, subject="Chicken gate restarted unexpectedly"):
                return
            time.sleep(EMAIL_RETRY_DELAY_S)

    threading.Thread(target=send, daemon=True).start()
