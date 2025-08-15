"""
Comprehensive unit tests for the Gate class.
Tests the core gate logic without hardware dependencies.
"""

import sys
import os
from unittest.mock import Mock, patch
import time

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chicken_gate.gate.gate import Gate
from chicken_gate.gate.gate_cmd import Cmd


class TestGateBasicFunctionality:
    """Test basic gate functionality without hardware"""

    def test_gate_initialization(self):
        """Test gate initializes with correct default values"""
        gate = Gate()
        assert gate.get_posn() == 100  # Default closed position
        assert gate.get_cmd() == Cmd.STOP
        assert not gate.is_opening()
        assert not gate.is_closing()
        assert not gate.is_moving()
        assert gate.get_errors() == []

    def test_gate_initialization_with_params(self):
        """Test gate initialization with custom parameters"""
        gate = Gate(init_posn=50, open_time=100, close_time=200)
        assert gate.get_posn() == 50
        assert gate.get_cmd() == Cmd.STOP

    def test_gate_open_command(self):
        """Test opening the gate"""
        gate = Gate(init_posn=100)  # Start closed
        gate.open()

        # Need to call tick() to process the command
        gate.tick()

        assert gate.is_opening()
        assert gate.get_cmd() == Cmd.OPEN
        assert not gate.is_closing()
        assert gate.is_moving()

    def test_gate_close_command(self):
        """Test closing the gate"""
        gate = Gate(init_posn=0)  # Start open
        gate.close()

        # Need to call tick() to process the command
        gate.tick()

        assert gate.is_closing()
        assert gate.get_cmd() == Cmd.CLOSE
        assert not gate.is_opening()
        assert gate.is_moving()

    def test_gate_stop_command(self):
        """Test stopping the gate"""
        gate = Gate()
        gate.open()
        gate.tick()  # Process open command
        assert gate.is_opening()

        gate.stop()
        gate.tick()  # Process stop command
        assert not gate.is_opening()
        assert not gate.is_closing()
        assert not gate.is_moving()
        assert gate.get_cmd() == Cmd.STOP


class TestGateMovement:
    """Test gate movement mechanics"""

    def test_gate_opens_over_time(self):
        """Test that gate position changes when opening"""
        gate = Gate(init_posn=100, open_time=10)  # 10 second open time
        gate.open()

        initial_position = gate.get_posn()

        # Simulate some time passing
        for _ in range(50):  # 5 seconds at 10Hz
            gate.tick()

        # Position should have decreased (opening)
        assert gate.get_posn() < initial_position

    def test_gate_closes_over_time(self):
        """Test that gate position changes when closing"""
        gate = Gate(init_posn=0, close_time=10)  # 10 second close time
        gate.close()

        initial_position = gate.get_posn()

        # Simulate some time passing
        for _ in range(50):  # 5 seconds at 10Hz
            gate.tick()

        # Position should have increased (closing)
        assert gate.get_posn() > initial_position

    def test_gate_stops_at_limits(self):
        """Test that gate stops at 0% and 100% positions"""
        # Test lower limit - patch the email to avoid network dependency
        with patch('chicken_gate.gate.gate.send_email'):
            gate = Gate(init_posn=5, open_time=1)  # Very fast opening
            gate.open()
            gate.tick()  # Process command

            # Run for enough time to reach 0%
            for _ in range(200):
                gate.tick()

            assert gate.get_posn() == 0
            assert gate.get_cmd() == Cmd.STOP

            # Test upper limit
            gate = Gate(init_posn=95, close_time=1)  # Very fast closing
            gate.close()
            gate.tick()  # Process command

            # Run for enough time to reach 100%
            for _ in range(200):
                gate.tick()

            assert gate.get_posn() == 100
            assert gate.get_cmd() == Cmd.STOP


class TestGateSwitches:
    """Test gate switch functionality"""

    def test_closed_switch_pressed(self):
        """Test closed switch detection"""
        gate = Gate()
        gate.set_closed_switch(True)
        gate.tick()

        # Gate should recognize closed position
        assert gate.get_posn() == 100

    def test_open_switch_pressed(self):
        """Test open switch detection"""
        gate = Gate()
        gate.set_open_switch(True)
        gate.tick()

        # Gate should recognize open position
        assert gate.get_posn() == 0

    def test_switch_overrides_movement(self):
        """Test that switches override movement commands"""
        gate = Gate(init_posn=50)
        gate.open()  # Start opening

        # Hit the open switch
        gate.set_open_switch(True)
        gate.tick()

        # Should stop and set position to 0
        assert gate.get_posn() == 0
        assert gate.get_cmd() == Cmd.STOP


class TestGateErrorHandling:
    """Test gate error handling and diagnostics"""

    def test_clear_errors(self):
        """Test clearing errors"""
        gate = Gate()

        # Simulate an error condition (this would be added by specific error logic)
        gate._Gate__errors.append("Test error")
        gate._Gate__open_disabled = True

        assert len(gate.get_errors()) == 1

        gate.clear_errors()
        assert len(gate.get_errors()) == 0

    def test_diagnostic_messages(self):
        """Test diagnostic message logging"""
        gate = Gate()

        # Test that diagnostic messages are tracked
        messages = gate.get_diagnostic_messages()
        assert isinstance(messages, list)

    def test_manual_stop_flag(self):
        """Test manual stop functionality"""
        gate = Gate()
        gate.open()

        # Manual stop should set flag and stop movement
        gate.stop()
        assert not gate.is_moving()


class TestGateReset:
    """Test gate position reset functionality"""

    def test_reset_position(self):
        """Test resetting gate to specific position"""
        gate = Gate(init_posn=50)

        gate.reset_posn_to(75)
        assert gate.get_posn() == 75

        gate.reset_posn_to(25)
        assert gate.get_posn() == 25

    def test_reset_position_bounds(self):
        """Test that reset position is bounded"""
        gate = Gate()

        # Test that positions are clamped to valid range
        gate.reset_posn_to(-10)
        assert gate.get_posn() >= 0

        gate.reset_posn_to(150)
        assert gate.get_posn() <= 100


class TestGateCommandQueuing:
    """Test gate command processing"""

    def test_command_changes(self):
        """Test that commands change gate state appropriately"""
        gate = Gate()

        # Test open command
        gate.open()
        gate.tick()  # Process command
        assert gate.get_cmd() == Cmd.OPEN

        # Test close command
        gate.close()
        gate.tick()  # Process command
        assert gate.get_cmd() == Cmd.CLOSE

        # Test stop command
        gate.stop()
        gate.tick()  # Process command
        assert gate.get_cmd() == Cmd.STOP

    def test_redundant_commands(self):
        """Test that redundant commands don't cause issues"""
        gate = Gate()

        gate.open()
        gate.tick()  # Process command
        first_cmd = gate.get_cmd()

        gate.open()  # Send same command again
        gate.tick()  # Process command
        second_cmd = gate.get_cmd()

        assert first_cmd == second_cmd == Cmd.OPEN


if __name__ == "__main__":
    try:
        import pytest
        pytest.main([__file__])
    except ImportError:
        print("pytest not available, running tests manually...")
        # Run tests manually here if needed
