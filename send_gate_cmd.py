#!/usr/bin/env python3
"""
Script to send commands to the chicken gate process.
Usage:
  python send_gate_cmd.py OPEN
  python send_gate_cmd.py CLOSE
  python send_gate_cmd.py RESET
  python send_gate_cmd.py RESET:50
"""

import sys


def send_command(command):
    """Send a command to the gate process by writing to a file."""
    valid_commands = ["OPEN", "CLOSE", "RESET"]

    # Handle RESET commands (RESET or RESET:position)
    if command.upper().startswith("RESET"):
        parts = command.upper().split(":")
        if len(parts) == 1:
            # Simple RESET command
            cmd_to_send = "RESET"
        elif len(parts) == 2:
            # RESET with position (RESET:50)
            try:
                position = int(parts[1])
                if 0 <= position <= 100:
                    cmd_to_send = f"RESET:{position}"
                else:
                    print(
                        f"Invalid position: {position}. Position must be between 0 and 100."
                    )
                    return False
            except ValueError:
                print(
                    f"Invalid position format: {parts[1]}. Position must be a number."
                )
                return False
        else:
            print(f"Invalid RESET command format: {command}")
            print("Valid formats: RESET or RESET:position (e.g., RESET:50)")
            return False
    else:
        # Regular OPEN/CLOSE commands
        if command.upper() not in valid_commands:
            print(f"Invalid command: {command}")
            print(f"Valid commands: {', '.join(valid_commands)}, RESET:position")
            return False
        cmd_to_send = command.upper()

    cmd_file = "gate_cmd.txt"
    try:
        with open(cmd_file, "w") as f:
            f.write(cmd_to_send)
        print(f"Command '{cmd_to_send}' sent to gate process")
        return True
    except IOError as e:
        print(f"Error writing command file: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python send_gate_cmd.py OPEN")
        print("  python send_gate_cmd.py CLOSE")
        print("  python send_gate_cmd.py RESET")
        print("  python send_gate_cmd.py RESET:position")
        print("Example: python send_gate_cmd.py RESET:50")
        sys.exit(1)

    command = sys.argv[1]
    success = send_command(command)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
