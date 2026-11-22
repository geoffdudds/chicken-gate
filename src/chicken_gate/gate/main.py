import contextlib
import json
import os
import time
from datetime import datetime

from .gate import Gate
from .gate_cmd import Cmd
from .gate_drv import Gate_drv
from .schedule import Schedule

# File paths for web interface communication
STATUS_FILE = "gate_status.json"


def write_gate_status(gate, schedule, schedule_enabled):
    """Write gate status to JSON file atomically"""
    try:
        status = gate.get_status()
        # Add timestamp
        status["last_updated"] = datetime.now().isoformat()

        # Add schedule information
        status["schedule"] = schedule.get_schedule_info()

        # Add schedule enabled status
        status["schedule_enabled"] = schedule_enabled

        # Write to temporary file first
        temp_file = STATUS_FILE + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(status, f)
        # Atomic rename
        os.rename(temp_file, STATUS_FILE)
    except Exception as e:
        print(f"Error writing status file: {e}")


def check_command_file():
    """Claim and read a pending command, if any.

    The file is renamed before reading so a command written by the web app
    while this one is being processed isn't deleted unread.
    """
    cmd_file = "gate_cmd.txt"
    claimed_file = cmd_file + ".processing"
    try:
        os.replace(cmd_file, claimed_file)
    except OSError:
        return None
    try:
        with open(claimed_file) as f:
            return f.read().strip()
    except OSError:
        return None
    finally:
        with contextlib.suppress(OSError):
            os.remove(claimed_file)


TICK_PERIOD = 0.1  # seconds
STATUS_WRITE_PERIOD = 1.0  # seconds; the web page polls every 2 s


def main():
    gate = Gate()
    gate_drv = Gate_drv(gate)
    schedule = Schedule()

    # Add schedule control flag here in main.py
    schedule_enabled = True  # Default to enabled

    print("Started chicken gate")

    last_tick = time.monotonic()
    next_tick = last_tick
    last_status_write = None

    while True:
        # push scheduled commands to driver (only if schedule is enabled)
        if schedule_enabled:
            sched_cmd = schedule.get_gate_cmd()
            if sched_cmd == Cmd.OPEN:
                print("sched cmd to open gate")
                gate_drv.open()
            elif sched_cmd == Cmd.CLOSE:
                print("sched cmd to close gate")
                gate_drv.close()

        # push shell & web commands to driver
        gate_cmd = check_command_file()
        if gate_cmd == "OPEN":
            print("cmd to open gate")
            gate_drv.open()
        elif gate_cmd == "CLOSE":
            print("cmd to close gate")
            gate_drv.close()
        elif gate_cmd == "STOP":
            print("cmd to stop gate")
            gate_drv.stop()
        elif gate_cmd == "ENABLE_SCHEDULE":
            print("cmd to enable schedule")
            schedule_enabled = True
        elif gate_cmd == "DISABLE_SCHEDULE":
            print("cmd to disable schedule")
            schedule_enabled = False
        elif gate_cmd == "CLEAR_ERRORS":
            print("shell cmd to clear errors")
            gate_drv.gate.clear_errors()
        elif gate_cmd == "CLEAR_DIAGNOSTICS":
            print("shell cmd to clear diagnostics")
            gate_drv.gate.clear_diagnostic_messages()
        elif gate_cmd and gate_cmd.startswith("RESET"):
            # Handle reset commands: RESET or RESET:position
            parts = gate_cmd.split(":")
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
                print(f"Invalid reset command format: {gate_cmd}")

        # Position is dead-reckoned from motor run time, so integrate over the
        # real elapsed time. Assuming a fixed 100 ms let the estimate fall
        # behind whenever a loop pass ran long, so the motor overran its target.
        now = time.monotonic()
        gate_drv.tick(now - last_tick)
        last_tick = now

        # Throttle status writes to spare the SD card, but write immediately
        # after a command so the web page reflects it on its next poll.
        if (
            gate_cmd
            or last_status_write is None
            or now - last_status_write >= STATUS_WRITE_PERIOD
        ):
            write_gate_status(gate_drv.gate, schedule, schedule_enabled)
            last_status_write = now

        next_tick += TICK_PERIOD
        # After a long stall, resume the normal cadence instead of bursting
        next_tick = max(next_tick, time.monotonic())
        time.sleep(max(0.0, next_tick - time.monotonic()))


if __name__ == "__main__":
    main()
