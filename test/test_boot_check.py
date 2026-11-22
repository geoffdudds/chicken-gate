"""Tests for detecting restarts without a clean shutdown."""

import pytest

from chicken_gate.gate import boot_check
from chicken_gate.shared import config


@pytest.fixture
def paths(tmp_path, monkeypatch):
    ram, sd = tmp_path / "ram", tmp_path / "sd"
    ram.mkdir()
    sd.mkdir()
    monkeypatch.setattr(config, "RAM_DIR", ram)
    monkeypatch.setattr(config, "PROJECT_ROOT", sd)
    return ram, sd


def reboot(ram):
    """A reboot clears RAM but not the SD card."""
    for f in ram.iterdir():
        f.unlink()


def test_unclean_reboot_detected_once(paths):
    assert boot_check.check_for_unexpected_restart(uptime_s=30)
    # A later service restart in the same boot isn't a Pi restart
    assert not boot_check.check_for_unexpected_restart(uptime_s=60)


def test_clean_reboot_not_reported(paths):
    ram, _ = paths
    boot_check.check_for_unexpected_restart(uptime_s=30)
    boot_check.record_clean_shutdown()
    reboot(ram)
    assert not boot_check.check_for_unexpected_restart(uptime_s=30)


def test_marker_is_consumed_so_a_later_hang_is_detected(paths):
    ram, _ = paths
    boot_check.record_clean_shutdown()
    boot_check.check_for_unexpected_restart(uptime_s=30)  # clean boot
    reboot(ram)  # hang: no clean shutdown recorded
    assert boot_check.check_for_unexpected_restart(uptime_s=30)


def test_first_start_long_after_boot_not_reported(paths):
    # e.g. the first deploy of this check onto a Pi that's been up for hours
    assert not boot_check.check_for_unexpected_restart(uptime_s=9 * 3600)
