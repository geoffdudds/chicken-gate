from src.timer import Timer
import pytest
import time


def test_tracks_elapsed_time():
    timer = Timer()
    timer.start()
    time.sleep(0.5)
    assert timer.get_time() == pytest.approx(0.5, abs=0.03)
    time.sleep(0.5)
    assert timer.get_time() == pytest.approx(1, abs=0.03)


def test_check_if_time_elapsed():
    timer = Timer()
    timer.start()
    time.sleep(0.5)
    assert timer.has_elapsed(0.48) == True
    assert timer.has_elapsed(0.52) == False


def test_time_since_last_read():
    timer = Timer()
    timer.start()
    print(timer)
    assert timer.get_since_last_read() == pytest.approx(0, abs=0.02)
    time.sleep(0.2)
    assert timer.get_since_last_read() == pytest.approx(0.2, abs=0.02)
    time.sleep(0.3)
    assert timer.get_since_last_read() == pytest.approx(0.3, abs=0.02)
