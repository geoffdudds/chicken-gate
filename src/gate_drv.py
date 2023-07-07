import RPi.GPIO as GPIO
from gpiozero import Button
from gate import Gate
from gate_cmd import Cmd


class Gate_drv:
    def __init__(self, gate: Gate):
        # set up io's
        self.closed_switch = Button(4)  # gate closed switch (physical pin 7)
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(4, GPIO.OUT)  # set Relay 1 output
        GPIO.setup(17, GPIO.OUT)  # set Relay 2 output

        self.gate = gate
        self.cmd = Cmd.STOP

    def tick(self):
        # set gate inputs
        # todo: add when switch is installed
        # self.gate.set_closed_switch(self.closed_switch.is_pressed)
        self.gate.set_closed_switch(False)
        self.gate.set_open_switch(False)

        # tick gate
        self.gate.tick()

        # get gate output
        self.cmd = self.gate.get_cmd()

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
        if posn != None:
            print(f"position reset to {posn}")
            self.gate.reset_posn_to(posn)

    def open(self):
        self.gate.open()

    def close(self):
        self.gate.close()

    def __turn_cw(self):
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)

    def __turn_ccw(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.HIGH)

    def __stop(self):
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)
