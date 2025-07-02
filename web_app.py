#!/usr/bin/env python3
"""
Flask web application for monitoring and controlling the chicken gate.
Provides a web interface to view gate position, switch status, and send commands.
"""

from flask import Flask, render_template, jsonify, request
import os
import json
from datetime import datetime

app = Flask(__name__)

def read_gate_status():
    """Read current gate status from the status file written by main.py"""
    try:
        status_file = "gate_status.json"
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                status = json.load(f)

            # The new format should have all the fields we need
            return {
                "position": status.get("position", 0),
                "target_position": status.get("target_position", 0),
                "is_opening": status.get("is_opening", False),
                "is_closing": status.get("is_closing", False),
                "is_moving": status.get("is_moving", False),
                "open_disabled": status.get("open_disabled", False),
                "closed_switch_pressed": status.get("closed_switch_pressed", False),
                "open_switch_pressed": status.get("open_switch_pressed", False),
                "errors": status.get("errors", []),
                "diagnostic_messages": status.get("diagnostic_messages", []),
                "last_updated": status.get("last_updated", datetime.now().isoformat())
            }
        else:
            # Return default status if file doesn't exist
            return {
                "position": 0,
                "target_position": 0,
                "is_opening": False,
                "is_closing": False,
                "is_moving": False,
                "open_disabled": False,
                "closed_switch_pressed": False,
                "open_switch_pressed": False,
                "errors": ["No status file found - is the gate system running?"],
                "diagnostic_messages": [],
                "last_updated": datetime.now().isoformat()
            }
    except Exception as e:
        # Fallback status if there's an error reading the file
        return {
            "position": 0,
            "target_position": 0,
            "is_opening": False,
            "is_closing": False,
            "is_moving": False,
            "open_disabled": False,
            "closed_switch_pressed": False,
            "open_switch_pressed": False,
            "errors": [f"Error reading status: {str(e)}"],
            "diagnostic_messages": [],
            "last_updated": datetime.now().isoformat()
        }

def send_gate_command(command):
    """Send a command to the gate by writing to the command file"""
    try:
        command_upper = command.upper()

        # Validate command
        valid_commands = ['OPEN', 'CLOSE', 'RESET', 'CLEAR_ERRORS']

        if command_upper.startswith('RESET:'):
            # Handle RESET:position format
            parts = command_upper.split(':')
            if len(parts) == 2:
                try:
                    position = int(parts[1])
                    if not (0 <= position <= 100):
                        return False, "Position must be between 0 and 100"
                except ValueError:
                    return False, "Invalid position format"
        elif command_upper not in valid_commands:
            return False, f"Unknown command: {command}"

        # Write command to file that main.py monitors
        cmd_file = "gate_cmd.txt"
        with open(cmd_file, "w") as f:
            f.write(command_upper)

        return True, f"Command '{command_upper}' sent to gate system"

    except Exception as e:
        return False, f"Failed to send command: {str(e)}"

@app.route('/')
def index():
    """Main page with gate control interface"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get current gate status"""
    status = read_gate_status()
    return jsonify(status)

@app.route('/api/command', methods=['POST'])
def api_command():
    """API endpoint to send commands to the gate"""
    data = request.get_json()

    if not data or 'command' not in data:
        return jsonify({'success': False, 'error': 'No command provided'}), 400

    command = data['command'].upper()
    valid_commands = ['OPEN', 'CLOSE', 'RESET', 'CLEAR_ERRORS']

    # Handle reset with position
    if command.startswith('RESET'):
        parts = command.split(':')
        if len(parts) == 2:
            try:
                position = int(parts[1])
                if not (0 <= position <= 100):
                    return jsonify({'success': False, 'error': 'Position must be between 0 and 100'}), 400
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid position format'}), 400
    elif command not in valid_commands:
        return jsonify({'success': False, 'error': f'Invalid command. Valid commands: {", ".join(valid_commands)}'}), 400

    result = send_gate_command(command)
    success, message = result if isinstance(result, tuple) else (result, f'Command "{command}" processed')

    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 500

@app.route('/api/history')
def api_history():
    """API endpoint to get command history (if implemented later)"""
    # Placeholder for future command history feature
    return jsonify({'history': []})

@app.route('/api/clear_diagnostics', methods=['POST'])
def api_clear_diagnostics():
    """API endpoint to clear diagnostic messages"""
    # Note: With the current file-based system, diagnostics are managed by main.py
    # This endpoint could be enhanced when diagnostic management is added to main.py
    return jsonify({'success': True, 'message': 'Diagnostics clearing not yet implemented in file-based system'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("Starting chicken gate web interface...")
    print("Open your browser to http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
