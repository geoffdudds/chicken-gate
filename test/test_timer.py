import os
import sys

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import time

import pytest

from chicken_gate.shared.timer import Timer


@pytest.mark.slow
def test_tracks_elapsed_time():
    timer = Timer()
    timer.start()
    time.sleep(0.5)
    assert timer.get_time() == pytest.approx(0.5, abs=0.03)
    time.sleep(0.5)
    assert timer.get_time() == pytest.approx(1, abs=0.03)


@pytest.mark.slow
def test_check_if_time_elapsed():
    timer = Timer()
    timer.start()
    time.sleep(0.5)
    assert timer.has_elapsed(0.48)
    assert not timer.has_elapsed(0.52)


@pytest.mark.slow
def test_time_since_last_read():
    timer = Timer()
    timer.start()
    print(timer)
    assert timer.get_since_last_read() == pytest.approx(0, abs=0.02)
    time.sleep(0.2)
    assert timer.get_since_last_read() == pytest.approx(0.2, abs=0.02)
    time.sleep(0.3)
    assert timer.get_since_last_read() == pytest.approx(0.3, abs=0.02)
