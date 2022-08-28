import pytest
import timer
import time


def test_works():
    tim = timer.Timer()
    tim.set_target(5)
    assert tim.is_at_target() == False

    for i in range(4):
        time.sleep(1)
        assert tim.is_at_target() == False

    time.sleep(1)
    assert tim.is_at_target() == True
