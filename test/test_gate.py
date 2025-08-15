import os
import sys
from unittest.mock import patch

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


from chicken_gate.gate.gate import Gate
from chicken_gate.gate.gate_cmd import Cmd


def test_100_percent_when_closed_switch_is_pressed():
    gate = Gate()
    gate.set_closed_switch(True)
    gate.set_open_switch(False)
    gate.tick()
    assert gate.get_posn() == 100


def test_0_percent_when_open_switch_is_pressed():
    gate = Gate()
    gate.set_closed_switch(False)
    gate.set_open_switch(True)
    gate.tick()
    assert gate.get_posn() == 0


def test_lowers_until_timeout():
    open_time = 330
    gate = Gate(open_time=open_time)
    gate.open()
    gate.tick()

    elapsed_time = 0
    while elapsed_time < open_time - 0.1:
        gate.tick()
        assert gate.get_cmd() == Cmd.OPEN
        elapsed_time += 0.1
    gate.tick(elapsed_time=0.2)
    assert gate.get_cmd() == Cmd.STOP


def test_closes_until_timeout():
    with patch("chicken_gate.gate.gate.send_email"):
        close_time = 390
        gate = Gate(init_posn=0, close_time=close_time)
        gate.close()
        gate.tick()

        elapsed_time = 0
        while elapsed_time < close_time - 0.1:
            gate.tick()
            assert gate.get_cmd() == Cmd.CLOSE
            elapsed_time += 0.1
        gate.tick(elapsed_time=0.2)
        assert gate.get_cmd() == Cmd.STOP


def test_reset_position():
    gate = Gate()
    gate.reset_posn_to(0)
    assert gate.get_posn() == 0
    gate.reset_posn_to(56)
    assert gate.get_posn() == 56
    gate.reset_posn_to(100)
    assert gate.get_posn() == 100
