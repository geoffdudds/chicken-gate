# from operator import truediv
# from typing import Callable

# import time
# from threading import Thread
from src.timer import Timer
from enum import Enum
from src.gate_cmd import Cmd


class Gate:
    def __init__(self, init_posn=100, open_time=330, close_time=390):
        self.__motion_cmd = Cmd.STOP
        self.__closed_switch_pressed = False
        self.__open_switch_pressed = False
        self.__posn = init_posn
        self.__posn_cmd = 100
        self.__open_rate = 100 / open_time
        self.__close_rate = 100 / close_time

    def get_cmd(self) -> Cmd:
        return self.__motion_cmd

    def get_posn(self):
        return self.__posn

    def tick(self, elapsed_time=0.1):
        # update position based on movement
        if self.__closed_switch_pressed:
            self.__posn = 100
        elif self.__open_switch_pressed:
            self.__posn = 0
        else:
            if self.__motion_cmd == Cmd.OPEN:
                self.__posn -= elapsed_time * self.__open_rate
            if self.__motion_cmd == Cmd.CLOSE:
                self.__posn += elapsed_time * self.__close_rate

            self.__posn = Gate.__clamp(self.__posn, 0, 100)

        # update target position (rx cmds)

        # update state
        if self.__posn_cmd < self.__posn:
            self.__motion_cmd = Cmd.OPEN
        elif self.__posn_cmd > self.__posn:
            self.__motion_cmd = Cmd.CLOSE
        else:
            self.__motion_cmd = Cmd.STOP

    def set_closed_switch(self, gate_closed_switch):
        self.__closed_switch_pressed = gate_closed_switch

    def set_open_switch(self, gate_open_switch):
        self.__open_switch_pressed = gate_open_switch

    def open(self):
        self.__posn_cmd = 0

    def close(self):
        self.__posn_cmd = 100

    def reset_posn_to(self, posn):
        self.__posn = Gate.__clamp(posn, 0, 100)

    def __clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n
