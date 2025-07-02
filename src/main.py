"""
todo: make the reset gate position use the enum instead of interger
todo: update the gate cmd button when the reset button is pressed
todo: update the gate cmd button when a scheduled cmd is executed
todo: make run as module so imports can work with pytest and program execution
"""

import time

ENABLE_APP = False

if ENABLE_APP:
    # wait for os to establish internet etc
    time.sleep(60)


from gate import Gate
from schedule import Schedule
if ENABLE_APP: from api import Api
from gate_drv import Gate_drv
from gate_cmd import Cmd
import errno
from email_me import send_email
import os
import json
from datetime import datetime


# from signal import signal, SIGPIPE, SIG_DFL
# signal(SIGPIPE,SIG_DFL)


def write_gate_status(gate_drv:Gate_drv):
    """Write current gate status to file for web interface"""
    try:
        status = {
            "position": gate_drv.get_posn(),
            "closed_switch": gate_drv.is_switch_pressed(),
            "open_switch": False,  # TODO: implement when open switch is installed
            "last_updated": datetime.now().isoformat(),
            "status": "Running"
        }

        with open("gate_status.json", "w") as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        print(f"Failed to write status file: {e}")


def check_command_file():
    """Check for commands in a file and remove the file after reading."""
    cmd_file = "gate_cmd.txt"
    if os.path.exists(cmd_file):
        try:
            with open(cmd_file, "r") as f:
                command = f.read().strip()
            os.remove(cmd_file)  # Remove after reading to prevent re-execution
            return command
        except (IOError, OSError):
            return None
    return None


def main():
    global tick_100ms
    pipe_error = False
    other_error = False
    gate = Gate()
    gate_drv = Gate_drv(gate)
    if ENABLE_APP:
        api = Api()
    schedule = Schedule()

    print("Started chicken gate")

    tick_100ms = 0
    next_tick = time.perf_counter()

    while True:
        now = time.perf_counter()
        if now >= next_tick:
            next_tick += 0.1
            tick_100ms += 1

        while tick_100ms > 0:
            tick_100ms -= 1

            if ENABLE_APP:
                if pipe_error is False and other_error is False:
                    try:
                        api.run()

                    except IOError as e:
                        if e.errno == errno.EPIPE:
                            print("Caught pipe error")
                            if pipe_error is False:
                                send_email("Pipe error")
                                pipe_error = True
                            print(e)
                        else:
                            print("Caught unhandled exception")
                            if other_error is False:
                                send_email("Some other error")
                                other_error = True
                            print(e)

                # push api commands to driver
                gate_drv.reset_posn_to(api.get_posn_reset())
                api_cmd = api.get_cmd()
                if api_cmd == Cmd.OPEN:
                    print("app cmd to open gate")
                    gate_drv.open()
                elif api_cmd == Cmd.CLOSE:
                    print("app cmd to close gate")
                    gate_drv.close()

            # push api commands to driver
            sched_cmd = schedule.get_gate_cmd()
            if sched_cmd == Cmd.OPEN:
                print("sched cmd to open gate")
                gate_drv.open()
            elif sched_cmd == Cmd.CLOSE:
                print("sched cmd to close gate")
                gate_drv.close()

            # push shell commands to driver
            shell_cmd = check_command_file()
            if shell_cmd == "OPEN":
                print("shell cmd to open gate")
                gate_drv.open()
            elif shell_cmd == "CLOSE":
                print("shell cmd to close gate")
                gate_drv.close()
            elif shell_cmd and shell_cmd.startswith("RESET"):
                # Handle reset commands: RESET or RESET:position
                parts = shell_cmd.split(":")
                if len(parts) == 1:
                    # RESET - reset to current switch position (100 if closed, 0 if open)
                    reset_pos = 100 if gate_drv.is_switch_pressed() else 0
                    print(f"shell cmd to reset gate position to {reset_pos}")
                    gate_drv.reset_posn_to(reset_pos)
                elif len(parts) == 2:
                    # RESET:position - reset to specific position
                    try:
                        reset_pos = int(parts[1])
                        print(f"shell cmd to reset gate position to {reset_pos}")
                        gate_drv.reset_posn_to(reset_pos)
                    except ValueError:
                        print(f"Invalid reset position: {parts[1]}")
                else:
                    print(f"Invalid reset command format: {shell_cmd}")

            gate_drv.tick()

            # Write status for web interface
            write_gate_status(gate_drv)

            if ENABLE_APP:
                api.set_posn(gate_drv.get_posn())
            write_gate_status(gate_drv)


if __name__ == "__main__":
    main()
