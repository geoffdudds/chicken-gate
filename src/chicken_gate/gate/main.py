import time
import os
import json
from datetime import datetime

from .gate import Gate
from .schedule import Schedule
from .gate_drv import Gate_drv
from .gate_cmd import Cmd


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
            json.dump(status, f, indent=2)
        # Atomic rename
        os.rename(temp_file, STATUS_FILE)
    except Exception as e:
        print(f"Error writing status file: {e}")


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
    gate = Gate()
    gate_drv = Gate_drv(gate)
    schedule = Schedule()

    # Add schedule control flag here in main.py
    schedule_enabled = True  # Default to enabled

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

            gate_drv.tick()

            # Write status for web interface - pass the gate object, not gate_drv
            write_gate_status(gate_drv.gate, schedule, schedule_enabled)


if __name__ == "__main__":
    main()
