from gate_cmd import Cmd
from email_me import send_email


class Gate:
    def __init__(
        self, init_posn: float = 100, open_time: float = 330, close_time: float = 400
    ):
        self.__motion_cmd = Cmd.STOP
        self.__closed_switch_pressed = False
        self.__open_switch_pressed = False
        self.__posn: float = init_posn
        self.__posn_cmd: float = 100
        self.__open_rate: float = 100 / open_time
        self.__close_rate: float = 100 / close_time

    def get_cmd(self) -> Cmd:
        return self.__motion_cmd

    def get_posn(self):
        return self.__posn

    def tick(self, elapsed_time=0.1):
        # update position based on movement
        if self.__closed_switch_pressed:
            self.__posn = min(90, self.__posn)
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
            if self.__motion_cmd is not Cmd.OPEN:
                print("gate entering OPEN state")
            self.__motion_cmd = Cmd.OPEN
        elif self.__posn_cmd > self.__posn:
            if self.__motion_cmd is not Cmd.CLOSE:
                print("gate entering CLOSE state")
            self.__motion_cmd = Cmd.CLOSE
        else:
            if self.__motion_cmd is not Cmd.STOP:
                print("gate entering STOP state")

                # alert if finished closing but closed switch is not pressed
                if self.__motion_cmd == Cmd.CLOSE and not self.__closed_switch_pressed:
                    msg: str = "gate finished closing but closed switch is not pressed"
                    print(msg)
                    send_email(msg)

                # alert if finished opening but closed switch is still pressed
                if self.__motion_cmd == Cmd.OPEN and self.__closed_switch_pressed:
                    msg: str = (
                        "gate finished opening but closed switch is still pressed"
                    )
                    print(msg)
                    send_email(msg)

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
        self.__posn_cmd = self.__posn

    @staticmethod
    def __clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n
