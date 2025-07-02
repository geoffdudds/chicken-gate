from gate_cmd import Cmd
from email_me import send_email
import logging

# Configure logging for system journal
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logger = logging.getLogger('chicken-gate')


class Gate:
    def __init__(self, init_posn=100, open_time=330, close_time=420):
        self.__motion_cmd = Cmd.STOP
        self.__closed_switch_pressed = False
        self.__open_switch_pressed = False
        self.__posn: float = init_posn
        self.__posn_cmd: float = 100
        self.__open_rate: float = 100 / open_time
        self.__close_rate: float = 100 / close_time
        self.__errors = []  # List to store error messages
        self.__open_disabled = False  # Flag to disable opening when error occurs
        self.__diagnostic_messages = []  # List to store diagnostic/status messages

    def get_cmd(self) -> Cmd:
        return self.__motion_cmd

    def get_posn(self):
        return self.__posn

    def is_opening(self) -> bool:
        """Returns True if gate is currently opening"""
        return self.__motion_cmd == Cmd.OPEN

    def is_closing(self) -> bool:
        """Returns True if gate is currently closing"""
        return self.__motion_cmd == Cmd.CLOSE

    def is_moving(self) -> bool:
        """Returns True if gate is currently moving (opening or closing)"""
        return self.__motion_cmd != Cmd.STOP

    def get_errors(self) -> list:
        """Returns list of current error messages"""
        return self.__errors.copy()

    def clear_errors(self):
        """Clear all error messages and re-enable opening"""
        error_count = len(self.__errors)
        self.__errors.clear()
        self.__open_disabled = False
        if error_count > 0:
            self.__add_diagnostic(f"cleared {error_count} error(s) - gate opening re-enabled")

    def get_diagnostic_messages(self) -> list:
        """Returns list of recent diagnostic messages for website display"""
        return self.__diagnostic_messages.copy()

    def clear_diagnostic_messages(self):
        """Clear diagnostic messages"""
        self.__diagnostic_messages.clear()

    def get_status(self) -> dict:
        """Returns comprehensive status for website API"""
        return {
            "position": self.__posn,
            "target_position": self.__posn_cmd,
            "is_opening": self.is_opening(),
            "is_closing": self.is_closing(),
            "is_moving": self.is_moving(),
            "open_disabled": self.__open_disabled,
            "closed_switch_pressed": self.__closed_switch_pressed,
            "open_switch_pressed": self.__open_switch_pressed,
            "errors": self.get_errors(),
            "diagnostic_messages": self.get_diagnostic_messages()
        }

    def tick(self, elapsed_time=0.1):
        # update position based on movement
        if self.__closed_switch_pressed:
            self.__posn = max(90, self.__posn)

        if self.__open_switch_pressed:
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
            # Don't allow opening if disabled due to error
            if self.__open_disabled:
                self.__motion_cmd = Cmd.STOP
            else:
                if self.__motion_cmd is not Cmd.OPEN:
                    self.__add_diagnostic("gate entering OPEN state")
                self.__motion_cmd = Cmd.OPEN

                if self.get_posn() < 90 and self.__closed_switch_pressed:
                    msg: str = "gate position is below 90 but closed switch is pressed"
                    self.__add_diagnostic(f"ERROR: {msg}")
                    send_email(msg)
                    self.__add_error(msg)
                    self.__open_disabled = True  # Disable opening
                    self.__motion_cmd = Cmd.STOP  # Stop immediately
        elif self.__posn_cmd > self.__posn:
            if self.__motion_cmd is not Cmd.CLOSE:
                self.__add_diagnostic("gate entering CLOSE state")
            self.__motion_cmd = Cmd.CLOSE
        else:
            if self.__motion_cmd is not Cmd.STOP:
                self.__add_diagnostic("gate entering STOP state")

                # alert if finished closing but closed switch is not pressed
                if self.__motion_cmd == Cmd.CLOSE and not self.__closed_switch_pressed:
                    msg: str = "gate finished closing but closed switch is not pressed"
                    self.__add_diagnostic(f"ERROR: {msg}")
                    send_email(msg)
                    self.__add_error(msg)

                # alert if finished opening but closed switch is still pressed
                if self.__motion_cmd == Cmd.OPEN and self.__closed_switch_pressed:
                    msg: str = (
                        "gate finished opening but closed switch is still pressed"
                    )
                    self.__add_diagnostic(f"ERROR: {msg}")
                    send_email(msg)
                    self.__add_error(msg)

            self.__motion_cmd = Cmd.STOP

    def set_closed_switch(self, gate_closed_switch):
        self.__closed_switch_pressed = gate_closed_switch

    def set_open_switch(self, gate_open_switch):
        self.__open_switch_pressed = gate_open_switch

    def open(self):
        """Open the gate if not disabled due to errors"""
        if not self.__open_disabled:
            self.__posn_cmd = 0
            self.__add_diagnostic("gate open command received")
        else:
            self.__add_diagnostic("gate open command rejected - errors present")

    def close(self):
        self.__posn_cmd = 100
        self.__add_diagnostic("gate close command received")

    def reset_posn_to(self, posn):
        self.__posn = Gate.__clamp(posn, 0, 100)
        self.__posn_cmd = self.__posn
        self.__add_diagnostic(f"position reset to {self.__posn}")

    def __add_error(self, error_msg: str):
        """Add an error message to the error list"""
        if error_msg not in self.__errors:
            self.__errors.append(error_msg)

    def __add_diagnostic(self, diagnostic_msg: str):
        """Add a diagnostic message to the diagnostic list (keep last 20) and log to system"""
        from datetime import datetime
        timestamped_msg = f"{datetime.now().strftime('%H:%M:%S')}: {diagnostic_msg}"
        self.__diagnostic_messages.append(timestamped_msg)

        # Keep only the last 20 messages to prevent memory buildup
        if len(self.__diagnostic_messages) > 20:
            self.__diagnostic_messages.pop(0)

        # Print to console and log to system journal
        print(timestamped_msg)
        logger.info(diagnostic_msg)

    @staticmethod
    def __clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n
