"""
Integration tests for the complete gate system using mock hardware.
Tests the interaction between Gate and Gate_drv without RPi.GPIO dependency.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set testing environment before imports
os.environ["TESTING"] = "true"

from chicken_gate.gate.gate import Gate
from chicken_gate.gate.gate_cmd import Cmd
from chicken_gate.gate.gate_drv_mock import Gate_drv

# The mock_email_send fixture is now provided by conftest.py
# and automatically available to all tests


class TestGateDriverIntegration:
    """Test integration between Gate and Gate_drv using mock hardware"""

    def setup_method(self):
        """Set up test environment for each test"""
        self.gate = Gate(init_posn=0, open_time=10, close_time=10)
        self.driver = Gate_drv(
            self.gate, initial_closed_switch=False, initial_open_switch=False
        )

    def test_driver_initialization(self):
        """Test that driver initializes correctly with gate"""
        assert self.gate.get_posn() == 0  # Should start at 0 (open)
        assert self.driver.cmd == Cmd.STOP

        relays = self.driver.get_relay_states()
        assert not relays["relay1"]
        assert not relays["relay2"]

    def test_driver_initialization_with_closed_switch(self):
        """Test driver initialization when closed switch is pressed"""
        gate = Gate(init_posn=0, open_time=10, close_time=10)
        driver = Gate_drv(gate, initial_closed_switch=True)

        # Should reset to closed position (100)
        assert gate.get_posn() == 100

    def test_opening_sequence(self):
        """Test complete opening sequence"""
        # Start with gate closed
        self.gate.reset_posn_to(100)

        # Send open command
        self.gate.open()

        # Process through driver
        self.driver.tick()

        # Check that relays are set correctly for opening
        relays = self.driver.get_relay_states()
        assert relays["relay1"]  # Open relay should be on
        assert not relays["relay2"]  # Close relay should be off

        # Simulate movement over time
        initial_position = self.gate.get_posn()
        for _ in range(50):  # Simulate 5 seconds
            self.driver.tick()

        # Position should have decreased (opening)
        assert self.gate.get_posn() < initial_position

    def test_closing_sequence(self):
        """Test complete closing sequence"""
        # Start with gate open
        self.gate.reset_posn_to(0)

        # Send close command
        self.gate.close()

        # Process through driver
        self.driver.tick()

        # Check that relays are set correctly for closing
        relays = self.driver.get_relay_states()
        assert not relays["relay1"]  # Open relay should be off
        assert relays["relay2"]  # Close relay should be on

        # Simulate movement over time
        initial_position = self.gate.get_posn()
        for _ in range(50):  # Simulate 5 seconds
            self.driver.tick()

        # Position should have increased (closing)
        assert self.gate.get_posn() > initial_position

    def test_stop_sequence(self):
        """Test stopping the gate during movement"""
        # Start opening
        self.gate.reset_posn_to(100)
        self.gate.open()
        self.driver.tick()

        # Verify it's opening
        assert self.gate.is_opening()
        relays = self.driver.get_relay_states()
        assert relays["relay1"]

        # Stop the gate
        self.gate.stop()
        self.driver.tick()

        # Verify it stopped
        assert not self.gate.is_moving()
        relays = self.driver.get_relay_states()
        assert not relays["relay1"]
        assert not relays["relay2"]

    def test_switch_detection(self):
        """Test that the closed switch is properly detected"""
        # Start with gate closed (target position = 100) to avoid movement
        self.gate.close()

        # Test closed switch
        self.driver.set_switch_state(closed_pressed=True)
        self.driver.tick()
        # When closed switch is pressed, position is set to max(90, current_position)
        # Since gate target is 100 (closed), no movement should occur
        assert self.gate.get_posn() >= 90

        # Test closed switch released
        self.driver.set_switch_state(closed_pressed=False)
        self.driver.tick()
        # Position should remain where it was (no movement since target is still 100)
        assert self.gate.get_posn() >= 90

    def test_switch_stops_movement(self):
        """Test that hitting a switch affects movement"""
        # Start with gate partially open
        self.gate.reset_posn_to(50)

        # Start closing
        self.gate.close()
        self.driver.tick()
        assert self.gate.is_closing()

        # Hit the closed switch
        self.driver.set_switch_state(closed_pressed=True)
        self.driver.tick()

        # Closed switch sets position to max(90, current), but target is still 100
        # So gate continues closing until it reaches 100
        position_after_switch = self.gate.get_posn()
        assert position_after_switch >= 90  # Should be at least 90 due to closed switch

        # Let it continue to reach the target
        max_ticks = 50
        tick_count = 0
        while self.gate.is_moving() and tick_count < max_ticks:
            self.driver.tick()
            tick_count += 1

        # Should eventually reach target and stop
        assert not self.gate.is_moving()
        assert self.gate.get_posn() == 100

    def test_relay_state_transitions(self):
        """Test that relay states transition correctly"""
        # Start with gate at closed position so opening will trigger movement
        self.gate.reset_posn_to(100)

        relays = self.driver.get_relay_states()

        # Initially both relays should be off
        assert not relays["relay1"]
        assert not relays["relay2"]

        # Start opening
        self.gate.open()
        self.driver.tick()
        relays = self.driver.get_relay_states()
        assert relays["relay1"]
        assert not relays["relay2"]

        # Switch to closing
        self.gate.close()
        self.driver.tick()
        relays = self.driver.get_relay_states()
        assert not relays["relay1"]
        assert relays["relay2"]

        # Stop
        self.gate.stop()
        self.driver.tick()
        relays = self.driver.get_relay_states()
        assert not relays["relay1"]
        assert not relays["relay2"]


class TestGateDriverRealTimeSimulation:
    """Test gate behavior in real-time-like scenarios"""

    @pytest.mark.slow
    def test_full_open_cycle(self):
        """Test a complete open cycle from closed to open"""
        gate = Gate(init_posn=100, open_time=5, close_time=5)  # 5-second cycles
        driver = Gate_drv(gate)

        # Start opening
        gate.open()

        # Simulate until gate reaches open position
        max_ticks = 200  # Safety limit
        tick_count = 0

        while gate.is_moving() and tick_count < max_ticks:
            driver.tick()
            tick_count += 1

        # Should have reached open position
        assert gate.get_posn() == 0
        assert not gate.is_moving()
        assert tick_count < max_ticks  # Didn't hit safety limit

    @pytest.mark.slow
    @patch("chicken_gate.gate.email_me.send_email")
    def test_full_close_cycle(self, mock_send_email):
        """Test a complete close cycle from open to closed"""
        gate = Gate(init_posn=0, open_time=5, close_time=5)  # 5-second cycles
        driver = Gate_drv(gate)

        # Start closing
        gate.close()
        driver.tick()  # Process the close command

        # Simulate until gate reaches closed position
        max_ticks = 200  # Safety limit
        tick_count = 0

        while gate.is_moving() and tick_count < max_ticks:
            driver.tick()
            tick_count += 1

        # Should have reached closed position
        assert gate.get_posn() == 100
        assert not gate.is_moving()
        assert tick_count < max_ticks  # Didn't hit safety limit

    def test_emergency_stop_during_movement(self):
        """Test emergency stop functionality"""
        gate = Gate(init_posn=100, open_time=10, close_time=10)  # Start closed
        driver = Gate_drv(gate, auto_reset_position=False)  # Don't auto-reset position

        # Start opening (from 100 to 0)
        gate.open()
        driver.tick()  # Process the open command

        # Let it move partway
        for _ in range(25):  # About 2.5 seconds
            driver.tick()

        position_before_stop = gate.get_posn()
        assert gate.is_opening()
        assert 0 < position_before_stop < 100

        # Emergency stop
        gate.stop()
        driver.tick()

        # Should stop immediately
        assert not gate.is_moving()
        assert gate.get_posn() == position_before_stop


class TestErrorConditions:
    """Test error handling in the integrated system"""

    def test_conflicting_switch_states(self):
        """Test behavior when both switches are pressed (should not happen)"""
        gate = Gate()
        driver = Gate_drv(gate)

        # Set both switches pressed (error condition)
        driver.set_switch_state(closed_pressed=True, open_pressed=True)
        driver.tick()

        # Gate should handle this gracefully (implementation dependent)
        # At minimum, it shouldn't crash
        assert isinstance(gate.get_posn(), (int, float))


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    test_classes = [
        TestGateDriverIntegration,
        TestGateDriverRealTimeSimulation,
        TestErrorConditions,
    ]

    for test_class in test_classes:
        print(f"Running {test_class.__name__}...")
        instance = test_class()

        # Run setup if it exists
        if hasattr(instance, "setup_method"):
            instance.setup_method()

        # Run all test methods
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                print(f"  {method_name}...")
                method = getattr(instance, method_name)
                try:
                    method()
                    print("    ✓ PASSED")
                except Exception as e:
                    print(f"    ✗ FAILED: {e}")

        print()

    print("Test run complete.")
