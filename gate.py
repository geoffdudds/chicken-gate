from typing import Callable
import RPi.GPIO as GPIO
from gpiozero import Button
import time
from threading import Thread


class Gate:
    def __init__(self):
        self.switch = Button(4)  # gate closed switch (physical pin 7)
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(4, GPIO.OUT)  # set Relay 1 output
        GPIO.setup(17, GPIO.OUT)  # set Relay 2 output
        self.gate_position_fbk_cb = None
        self.cmd = None
        self.cmd_thread = Thread(target=self.process_inputs)
        self.cmd_thread.start()

    def set_position_fbk_cbk(self, gate_position_fbk_cb):
        self.gate_position_fbk_cb = gate_position_fbk_cb

    def process_inputs(self):
        if self.cmd is "lift":
            self.process_lift()
        elif self.cmd is "lower":
            self.process_lower()

    def lift(self):
        self.cmd = "lift"

    def lower(self):
        self.cmd = "lower"

    def process_lift(self):
        self.turn_cw()
        self.wait_until_raised()
        self.stop()

    def process_lower(self):
        self.turn_ccw()
        self.wait_until_lowered()
        self.stop()

    def turn_cw(self):
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)

    def turn_ccw(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.HIGH)

    def stop(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)

    def wait_until_raised(self):
        self.run_position_fbk_cb(50)
        self.switch.wait_for_press()
        self.run_position_fbk_cb(100)

    def wait_until_lowered(self):
        lower_time = 30
        for t in range(lower_time):
            time.sleep(1)
            self.run_position_fbk_cb(((lower_time - t) / lower_time) * 100)

    def run_position_fbk_cb(self, position):
        cb = self.gate_position_fbk_cb
        if cb is not None:
            cb(position)
