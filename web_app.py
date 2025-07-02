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

# Configuration
STATUS_FILE = "gate_status.json"
COMMAND_FILE = "gate_cmd.txt"

def read_gate_status():
    """Read current gate status from file"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
    except (IOError, json.JSONDecodeError):
        pass

    # Default status if file doesn't exist or is invalid
    return {
        "position": 0,
        "closed_switch": False,
        "open_switch": False,
        "last_updated": datetime.now().isoformat(),
        "status": "Unknown"
    }

def send_gate_command(command):
    """Send a command to the gate process"""
    try:
        with open(COMMAND_FILE, 'w') as f:
            f.write(command.upper())
        return True
    except IOError:
        return False

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
    valid_commands = ['OPEN', 'CLOSE', 'RESET']

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

    success = send_gate_command(command)

    if success:
        return jsonify({'success': True, 'message': f'Command "{command}" sent successfully'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send command'}), 500

@app.route('/api/history')
def api_history():
    """API endpoint to get command history (if implemented later)"""
    # Placeholder for future command history feature
    return jsonify({'history': []})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("Starting chicken gate web interface...")
    print("Open your browser to http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
