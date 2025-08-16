import RPi.GPIO as GPIO

from .gate import Gate
from .gate_cmd import Cmd


class Gate_drv:
    def __init__(self, gate: Gate):
        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # GPIO pin assignments
        self.CLOSED_SWITCH_PIN = 2  # physical pin 3, GPIO 2
        self.RELAY1_PIN = 4  # physical pin 7, GPIO 4
        self.RELAY2_PIN = 17  # physical pin 11, GPIO 17

        # Set up switch input with pull-up (normally closed switch)
        GPIO.setup(self.CLOSED_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Set up relay outputs
        GPIO.setup(self.RELAY1_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.RELAY2_PIN, GPIO.OUT, initial=GPIO.LOW)

        self.gate = gate
        self.cmd = Cmd.STOP
        self.__prev_cmd = Cmd.NONE

        # reset gate position to 100 if closed switch is pressed, else 0
        # For normally closed switch: pressed = True when button reads HIGH
        self.reset_posn_to(100 if self.is_switch_pressed() else 0)

    def is_switch_pressed(self):
        """
        Helper method to handle normally closed switch logic.
        Normally closed switch with pull-up:
        - Switch not pressed (closed) = GPIO reads LOW → gate NOT closed
        - Switch pressed (opened) = GPIO reads HIGH → gate IS closed

        Since this is backwards from what we want, we need to invert the logic.
        When the gate is physically closed, the switch opens and GPIO goes HIGH.
        """
        # Read GPIO pin - HIGH means switch is pressed (opened)
        return GPIO.input(self.CLOSED_SWITCH_PIN) == GPIO.HIGH

    def tick(self):
        # set gate inputs - using helper method for clarity
        self.gate.set_closed_switch(self.is_switch_pressed())
        # todo: add when switch is installed
        self.gate.set_open_switch(False)

        # tick gate
        self.gate.tick()

        # get gate output
        self.cmd = self.gate.get_cmd()

        # only update outputs on change
        if self.cmd != self.__prev_cmd:
            self.__prev_cmd = self.cmd

            # drive gate according to gate output
            if self.cmd == Cmd.OPEN:
                self.__turn_ccw()
            elif self.cmd == Cmd.CLOSE:
                self.__turn_cw()
            else:
                self.__stop()

    def get_posn(self):
        return self.gate.get_posn()

    def reset_posn_to(self, posn):
        if posn is not None:
            print(f"position reset to {posn}")
            self.gate.reset_posn_to(posn)

    def open(self):
        self.gate.open()

    def close(self):
        self.gate.close()

    def stop(self):
        self.gate.stop()

    def __turn_cw(self):
        GPIO.output(self.RELAY1_PIN, GPIO.HIGH)
        GPIO.output(self.RELAY2_PIN, GPIO.LOW)

    def __turn_ccw(self):
        GPIO.output(self.RELAY1_PIN, GPIO.LOW)
        GPIO.output(self.RELAY2_PIN, GPIO.HIGH)

    def __stop(self):
        GPIO.output(self.RELAY1_PIN, GPIO.LOW)
        GPIO.output(self.RELAY2_PIN, GPIO.LOW)

    def cleanup(self):
        """Clean up GPIO resources when shutting down"""
        GPIO.cleanup()
