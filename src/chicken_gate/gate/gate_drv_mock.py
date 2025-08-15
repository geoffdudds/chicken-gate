"""
Mock implementation of Gate_drv for testing purposes.
This replaces the RPi.GPIO dependency with a simulated interface.
"""

from .gate import Gate
from .gate_cmd import Cmd
import logging

logger = logging.getLogger('chicken-gate-mock')


class Gate_drv:
    """Mock gate driver that simulates hardware without RPi.GPIO dependency"""

    def __init__(self, gate: Gate, initial_closed_switch=False, initial_open_switch=False, auto_reset_position=True):
        # Simulate GPIO pin assignments (no actual GPIO setup)
        self.CLOSED_SWITCH_PIN = 2
        self.RELAY1_PIN = 4
        self.RELAY2_PIN = 17

        self.gate = gate
        self.cmd = Cmd.STOP
        self.__prev_cmd = Cmd.NONE

        # Mock switch states - only closed switch exists in real hardware
        self._closed_switch_state = initial_closed_switch
        # Note: initial_open_switch parameter kept for compatibility but not used

        # Track relay states for testing
        self._relay1_state = False
        self._relay2_state = False

        # Auto-reset position based on initial switch state if requested
        if auto_reset_position:
            # If closed switch is pressed, assume gate is at 100%, else assume 0%
            self.reset_posn_to(100 if self._closed_switch_state else 0)

        logger.info("Mock Gate_drv initialized")

    def is_switch_pressed(self):
        """Mock version of switch reading"""
        return self._closed_switch_state

    def set_switch_state(self, closed_pressed=None, open_pressed=None):
        """Test helper to simulate switch state changes"""
        if closed_pressed is not None:
            self._closed_switch_state = closed_pressed
            self._manual_switch_override = True
        # open_pressed parameter kept for compatibility but ignored (no open switch in real hardware)

    def get_relay_states(self):
        """Test helper to check relay states"""
        return {
            'relay1': self._relay1_state,
            'relay2': self._relay2_state
        }

    def tick(self):
        # Auto-simulate closed switch activation BEFORE calling gate.tick() (unless manually overridden)
        if not hasattr(self, '_manual_switch_override'):
            gate_position = self.gate.get_posn()
            # Closed switch activates at ~95% closed (position >= 95)
            # This simulates the physical switch being pressed when gate is almost fully closed
            self._closed_switch_state = gate_position >= 95
            
        # Set gate inputs using mock states
        self.gate.set_closed_switch(self.is_switch_pressed())
        # No open switch in real hardware - gate uses only closed switch feedback
        self.gate.set_open_switch(False)  # Always False since no open switch exists

        # Update gate logic
        self.gate.tick()

        # Get command from gate
        self.cmd = self.gate.get_cmd()

        # Handle relay control (mock version)
        if self.cmd == Cmd.OPEN:
            if self.__prev_cmd != Cmd.OPEN:
                logger.info("Mock: Starting to open gate (RELAY1=ON, RELAY2=OFF)")
                self._relay1_state = True
                self._relay2_state = False
        elif self.cmd == Cmd.CLOSE:
            if self.__prev_cmd != Cmd.CLOSE:
                logger.info("Mock: Starting to close gate (RELAY1=OFF, RELAY2=ON)")
                self._relay1_state = False
                self._relay2_state = True
        else:  # STOP
            if self.__prev_cmd != Cmd.STOP:
                logger.info("Mock: Stopping gate (RELAY1=OFF, RELAY2=OFF)")
                self._relay1_state = False
                self._relay2_state = False

        self.__prev_cmd = self.cmd

    def reset_posn_to(self, position):
        """Reset gate position - delegates to gate object"""
        self.gate.reset_posn_to(position)
        logger.info(f"Mock: Gate position reset to {position}")

    def cleanup(self):
        """Mock cleanup - no actual GPIO cleanup needed"""
        logger.info("Mock: GPIO cleanup (no-op)")
        pass
