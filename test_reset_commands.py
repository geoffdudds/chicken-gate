#!/usr/bin/env python3
"""
Test script to verify the reset command functionality.
This simulates what the main.py will do when it receives reset commands.
"""

import os


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


def process_shell_command(shell_cmd):
    """Process shell commands including reset functionality"""
    if shell_cmd == "OPEN":
        print("shell cmd to open gate")
        return "OPEN"
    elif shell_cmd == "CLOSE":
        print("shell cmd to close gate")
        return "CLOSE"
    elif shell_cmd and shell_cmd.startswith("RESET"):
        # Handle reset commands: RESET or RESET:position
        parts = shell_cmd.split(":")
        if len(parts) == 1:
            # RESET - reset to current switch position (simulating closed switch)
            reset_pos = 100  # Simulate closed switch
            print(f"shell cmd to reset gate position to {reset_pos}")
            return f"RESET:{reset_pos}"
        elif len(parts) == 2:
            # RESET:position - reset to specific position
            try:
                reset_pos = int(parts[1])
                print(f"shell cmd to reset gate position to {reset_pos}")
                return f"RESET:{reset_pos}"
            except ValueError:
                print(f"Invalid reset position: {parts[1]}")
                return None
        else:
            print(f"Invalid reset command format: {shell_cmd}")
            return None
    return None


def test_commands():
    """Test various command scenarios"""
    test_cases = [
        "OPEN",
        "CLOSE",
        "RESET",
        "RESET:50",
        "RESET:0",
        "RESET:100",
        "RESET:invalid",
        "RESET:150",  # Out of range
        "INVALID",
    ]

    print("Testing shell command processing:")
    print("=" * 40)

    for cmd in test_cases:
        print(f"\nTesting command: '{cmd}'")
        # Write command to file
        with open("gate_cmd.txt", "w") as f:
            f.write(cmd)

        # Read and process command
        shell_cmd = check_command_file()
        result = process_shell_command(shell_cmd)
        print(f"Result: {result}")

    # Clean up any remaining file
    if os.path.exists("gate_cmd.txt"):
        os.remove("gate_cmd.txt")


if __name__ == "__main__":
    test_commands()
