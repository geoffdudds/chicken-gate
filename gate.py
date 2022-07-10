import RPi.GPIO as GPIO
from gpiozero import Button
import time


class Gate:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(4, GPIO.OUT)  # set Relay 1 output
        GPIO.setup(17, GPIO.OUT)  # set Relay 2 output

        self.switch = Button(4)

    def lift(self):
        self.turn_cw()
        self.wait_until_raised()
        self.stop()

    def lower(self):
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
        self.switch.wait_for_press()

    def wait_until_lowered(self):
        time.sleep(30)
