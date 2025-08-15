"""
Test configuration and utilities for chicken gate testing.
Handles mocking and dependency injection for hardware components.
"""

import os
import sys
from contextlib import contextmanager
from unittest.mock import Mock, patch


def is_raspberry_pi():
    """Check if we're running on a Raspberry Pi"""
    try:
        with open("/proc/cpuinfo") as f:
            return "BCM" in f.read()
    except Exception:
        return False


def is_testing_environment():
    """Check if we're in a testing environment"""
    return (
        "pytest" in sys.modules
        or "unittest" in sys.modules
        or os.environ.get("TESTING", "").lower() == "true"
        or not is_raspberry_pi()
    )


def setup_test_email_config():
    """Set up test email configuration via environment variables"""
    os.environ["CHICKEN_GATE_EMAIL_SENDER"] = "test@example.com"
    os.environ["CHICKEN_GATE_EMAIL_PASSWORD"] = "test_password"
    os.environ["CHICKEN_GATE_EMAIL_RECIPIENT"] = "test_recipient@example.com"


@contextmanager
def mock_rpi_gpio():
    """Context manager to mock RPi.GPIO for testing"""
    with patch.dict("sys.modules", {"RPi": Mock(), "RPi.GPIO": Mock()}):
        # Create a mock GPIO module with the expected interface
        mock_gpio = Mock()
        mock_gpio.BCM = 11
        mock_gpio.IN = 1
        mock_gpio.OUT = 0
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        mock_gpio.PUD_UP = 22

        # Mock methods
        mock_gpio.setmode = Mock()
        mock_gpio.setwarnings = Mock()
        mock_gpio.setup = Mock()
        mock_gpio.input = Mock(return_value=0)  # Default to LOW
        mock_gpio.output = Mock()
        mock_gpio.cleanup = Mock()

        sys.modules["RPi.GPIO"] = mock_gpio
        yield mock_gpio


def get_gate_driver_class():
    """Get the appropriate gate driver class based on environment"""
    if is_testing_environment():
        # Import from the chicken_gate package
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from chicken_gate.gate.gate_drv_mock import Gate_drv

        return Gate_drv
    else:
        from chicken_gate.gate.gate_drv import Gate_drv

        return Gate_drv


class GateTestHelper:
    """Helper class for testing gate functionality"""

    def __init__(self):
        self.mock_gpio = None

    def setup_mock_environment(self):
        """Set up a complete mock environment for testing"""
        if is_testing_environment():
            # Set testing flag
            os.environ["TESTING"] = "true"

            # Check if RPi.GPIO is available without importing it
            import importlib.util

            if importlib.util.find_spec("RPi.GPIO") is None:
                # RPi.GPIO not available, which is expected in test environment
                pass

    def create_test_gate_system(self, **kwargs):
        """Create a complete gate system suitable for testing"""
        # Import from the chicken_gate package
        import os
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from chicken_gate.gate.gate import Gate

        # Create gate with test-friendly defaults
        gate = Gate(
            init_posn=kwargs.get("init_posn", 0),
            open_time=kwargs.get("open_time", 10),  # Faster for tests
            close_time=kwargs.get("close_time", 10),  # Faster for tests
        )

        # Get appropriate driver class
        driver_class = get_gate_driver_class()

        # Create driver with test parameters
        driver = driver_class(
            gate,
            initial_closed_switch=kwargs.get("initial_closed_switch", False),
            initial_open_switch=kwargs.get("initial_open_switch", False),
        )

        return gate, driver

    def simulate_time_passage(self, gate, driver, seconds, tick_interval=0.1):
        """Simulate the passage of time for testing movement"""
        ticks = int(seconds / tick_interval)
        for _ in range(ticks):
            driver.tick()
        return ticks
