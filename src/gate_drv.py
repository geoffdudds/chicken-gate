from gpiozero import Button, OutputDevice
from gate import Gate
from gate_cmd import Cmd


class Gate_drv:
    def __init__(self, gate: Gate):
        # set up io's using gpiozero for all GPIO operations
        self.closed_switch = Button(2, pull_up=True, active_high=True)  # physical pin 3, GPIO 2

        # Use OutputDevice for relays
        self.relay1 = OutputDevice(4, initial_value=False)  # physical pin 7, GPIO 4
        self.relay2 = OutputDevice(17, initial_value=False)  # physical pin 11, GPIO 17

        self.gate = gate
        self.cmd = Cmd.STOP

        # reset gate position to 100 if closed switch is pressed, else 0
        self.reset_posn_to(100 if self.closed_switch.is_pressed else 0)

    def tick(self):
        # set gate inputs
        self.gate.set_closed_switch(self.closed_switch.is_pressed)
        # todo: add when switch is installed
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
        if posn is not None:
            print(f"position reset to {posn}")
            self.gate.reset_posn_to(posn)

    def open(self):
        self.gate.open()

    def close(self):
        self.gate.close()

    def __turn_cw(self):
        self.relay1.on()
        self.relay2.off()

    def __turn_ccw(self):
        self.relay1.off()
        self.relay2.on()

    def __stop(self):
        self.relay1.off()
        self.relay2.off()

    def cleanup(self):
        """Clean up GPIO resources when shutting down"""
        self.relay1.close()
        self.relay2.close()
        self.closed_switch.close()
