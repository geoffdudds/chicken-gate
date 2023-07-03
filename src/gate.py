# from operator import truediv
# from typing import Callable

# import time
# from threading import Thread
from src.timer import Timer
from enum import Enum


class Gate:
    class Cmd(Enum):
        STOP = 0
        CLOSE = 1
        OPEN = 2

    def __init__(self, init_posn=100, open_time=330, close_time=390):
        self.__motion_cmd = self.Cmd.STOP
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
            if self.__motion_cmd == self.Cmd.OPEN:
                self.__posn -= elapsed_time * self.__open_rate
            if self.__motion_cmd == self.Cmd.CLOSE:
                self.__posn += elapsed_time * self.__close_rate

            self.__posn = Gate.__clamp(self.__posn, 0, 100)

        # update target position (rx cmds)

        # update state
        if self.__posn_cmd < self.__posn:
            self.__motion_cmd = self.Cmd.OPEN
        elif self.__posn_cmd > self.__posn:
            self.__motion_cmd = self.Cmd.CLOSE
        else:
            self.__motion_cmd = self.Cmd.STOP

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

    # def init_position(self):
    #     # todo: init position better once switch is in
    #     # if self.switch.is_pressed:
    #     #     self.gate_timer.reset(self.time_to_lift)
    #     # else:
    #     #     self.gate_timer.reset(0)
    #     self.gate_timer.reset(self.time_to_lift)
    #     self.prev_position = self.get_position()

    # def reset(self, position):
    #     self.gate_timer.reset(position * self.time_to_lift / 100)
    #     self.prev_position = self.get_position()

    # def init_cmd(self):
    #     if self.is_raised():
    #         self.cmd = "lift"
    #     else:
    #         self.cmd = "lower"

    # def set_position_fbk_cb(self, gate_position_fbk_cb):
    #     self.gate_position_fbk_cb = gate_position_fbk_cb

    # def main(self):
    #     while True:
    #         self.process_inputs()

    # def process_inputs(self):
    #     if self.cmd is "lift":
    #         self.process_lift()
    #     elif self.cmd is "lower":
    #         self.process_lower()

    #     position = self.get_position()

    #     # if position != self.prev_position:
    #     #     self.is_moving = True
    #     # else:
    #     #     if self.is_moving:
    #     #         self.is_moving = False
    #     #         self.run_position_fbk_cb()
    #     #         print("Stopped at position: " + str(position) + "%")

    #     # self.prev_position = position

    #     if position != self.prev_position:
    #         if self.send_new_position_1hz():
    #             self.prev_position = position

    # def send_new_position_1hz(self) -> bool:
    #     if self.update_timer.is_at_target():
    #         self.update_timer.reset()
    #         self.update_timer.set_target(1)
    #         self.run_position_fbk_cb()
    #         return True
    #     return False

    # def lift(self):
    #     self.cmd = "lift"

    # def lower(self):
    #     self.cmd = "lower"

    # def process_lift(self):
    #     self.gate_timer.set_target(self.time_to_lift)
    #     if self.is_raised():
    #         self.stop()
    #     else:
    #         self.turn_cw()

    # def process_lower(self):
    #     self.gate_timer.set_target(0)
    #     if self.is_lowered():
    #         self.gate_timer.reset(0)
    #         self.stop()
    #     else:
    #         self.turn_ccw()

    # def is_raised(self):
    #     # todo: add once switch is in
    #     # if self.switch.is_pressed:
    #     #     self.gate_timer.reset(self.time_to_lift)
    #     return self.get_position() == 100

    # def is_lowered(self):
    #     return self.get_position() < 15

    # def get_position(self):
    #     return self.gate_timer.get_time() * 100 / self.time_to_lift

    # def run_position_fbk_cb(self):
    #     cb = self.gate_position_fbk_cb
    #     if cb is not None:
    #         cb(self.get_position())
