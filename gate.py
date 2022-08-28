from operator import truediv
from typing import Callable
import RPi.GPIO as GPIO
from gpiozero import Button
import time
import timer
from threading import Thread


class Gate:
    def __init__(self):
        self.switch = Button(4)  # gate closed switch (physical pin 7)
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(4, GPIO.OUT)  # set Relay 1 output
        GPIO.setup(17, GPIO.OUT)  # set Relay 2 output
        self.time_to_lift = 30
        self.gate_position_fbk_cb = None
        self.gate_position = 0
        self.prev_position = 0
        self.cmd = None
        self.gate_timer = timer.Timer()
        self.position_update_timer = timer.Timer()
        self.cmd_thread = Thread(target=self.main)
        self.cmd_thread.start()

    def set_position_fbk_cb(self, gate_position_fbk_cb):
        self.gate_position_fbk_cb = gate_position_fbk_cb

    def main(self):
        while True:
            self.process_inputs()

    def process_inputs(self):
        # print("thread runs")
        if self.cmd is "lift":
            self.process_lift()
        elif self.cmd is "lower":
            self.process_lower()

        position = self.get_position()

        if position != self.prev_position:
            self.send_new_position_1hz()
            self.prev_position = position

    def send_new_position_1hz(self):
        if self.position_update_timer.is_at_target():
            self.position_update_timer.set_target(self.position_update_timer.time + 1)
            self.run_position_fbk_cb()

    def lift(self):
        self.cmd = "lift"

    def lower(self):
        self.cmd = "lower"

    def process_lift(self):
        self.gate_timer.set_target(self.time_to_lift)
        if self.is_raised():
            self.stop()
            # print("lift stop")
        else:
            self.turn_cw()
            # print("lift cw")

    def process_lower(self):
        self.gate_timer.set_target(0)
        if self.is_lowered():
            self.stop()
            # print("lower stop")
        else:
            self.turn_ccw()
            # print("lower ccw")

    def turn_cw(self):
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)

    def turn_ccw(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.HIGH)

    def stop(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)

    def is_raised(self):
        # return self.switch.is_pressed() or self.get_position() == 100
        return self.get_position == 100

    def is_lowered(self):
        return self.gate_position == 0

    def get_position(self):
        return self.gate_timer.get_time() * 100 / self.time_to_lift

    def run_position_fbk_cb(self):
        cb = self.gate_position_fbk_cb
        if cb is not None:
            cb(self.get_position())
