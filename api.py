import BlynkLib
from BlynkTimer import BlynkTimer
from gate import Gate
from enum import Enum


class Api:
    class Cmd(Enum):
        STOP = 0
        CLOSE = 1
        OPEN = 2
        NONE = 3

    blynk: BlynkLib.Blynk = None

    def __init__(self):
        Api.blynk = BlynkLib.Blynk("3Ngd6Tdw9djI17trS1AfVY5aXfhlBwiz")
        self.timer = BlynkTimer()
        self.timer.set_interval(1, self.elapse_1s)
        self.__posn = 0
        self.__posn_reset = None
        self.__cmd = Api.Cmd.NONE

        # Register Virtual Pins
        @Api.blynk.on("V0")
        def v0_gate_cmd_write_handler(value):
            print("V0 gate command: {}".format(value))
            val = value.pop()
            if val == "0":
                self.__cmd = self.Cmd.OPEN
            elif val == "1":
                self.__cmd = self.Cmd.CLOSE
            else:
                print("invalid gate command")

        @Api.blynk.on("V1")
        def v1_gate_cmd_write_handler(value):
            print("V1 reset command: {}".format(value))
            val = value.pop()
            if val == "0":
                self.__posn_reset = 0
            elif val == "1":
                self.__posn_reset = 100
            else:
                print("invalid reset command")

    def set_posn(self, posn):
        self.__posn = posn

    def elapse_1s(self):
        # update gate position
        Api.blynk.virtual_write(3, self.__posn)

    def get_posn_reset(self):
        posn_reset = self.__posn_reset
        self.__posn_reset = None
        return posn_reset

    def get_cmd(self):
        cmd = self.__cmd
        self.__cmd = self.Cmd.NONE
        return cmd

    @blynk.on("V2")
    def v2_write_handler(value):
        pass

    def run(self):
        Api.blynk.run()
        self.timer.run()
