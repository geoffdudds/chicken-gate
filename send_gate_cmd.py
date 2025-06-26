#!/usr/bin/env python3
"""
Script to send commands to the chicken gate process.
Usage: python send_gate_cmd.py [OPEN|CLOSE]
"""

import sys


def send_command(command):
    """Send a command to the gate process by writing to a file."""
    valid_commands = ["OPEN", "CLOSE"]

    if command.upper() not in valid_commands:
        print(f"Invalid command: {command}")
        print(f"Valid commands: {', '.join(valid_commands)}")
        return False

    cmd_file = "gate_cmd.txt"
    try:
        with open(cmd_file, "w") as f:
            f.write(command.upper())
        print(f"Command '{command.upper()}' sent to gate process")
        return True
    except IOError as e:
        print(f"Error writing command file: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python send_gate_cmd.py [OPEN|CLOSE]")
        sys.exit(1)

    command = sys.argv[1]
    success = send_command(command)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
