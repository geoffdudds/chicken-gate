#!/usr/bin/env python3
"""
Flask web application for monitoring and controlling the chicken gate.
Provides a web interface to view gate position, switch status, and send commands.
"""

from flask import Flask, render_template, jsonify, request, Response
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)

# Camera configuration
CAMERA_IP = "192.168.0.135"
CAMERA_USERNAME = "chickencam"  # Default for Tapo cameras
CAMERA_PASSWORD = "password"       # You may need to set this up in camera settings

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
                "schedule": status.get("schedule", {}),
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
                "schedule": {},
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
            "schedule": {},
            "last_updated": datetime.now().isoformat()
        }

def send_gate_command(command):
    """Send a command to the gate by writing to the command file"""
    try:
        command_upper = command.upper()

        # Validate command
        valid_commands = ['OPEN', 'CLOSE', 'STOP', 'RESET', 'CLEAR_ERRORS', 'CLEAR_DIAGNOSTICS']

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

@app.route('/api/schedule')
def api_schedule():
    """API endpoint to get schedule information"""
    status = read_gate_status()
    schedule_info = status.get('schedule', {})
    return jsonify(schedule_info)

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Handle gate commands from the web interface"""
    try:
        data = request.get_json()
        command = data.get('command', '').upper()

        success, message = send_gate_command(command)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "message": message}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/history')
def api_history():
    """API endpoint to get command history (if implemented later)"""
    # Placeholder for future command history feature
    return jsonify({'history': []})

@app.route('/api/clear_diagnostics', methods=['POST'])
def api_clear_diagnostics():
    """API endpoint to clear diagnostic messages"""
    success, message = send_gate_command('CLEAR_DIAGNOSTICS')
    if success:
        return jsonify({'success': True, 'message': 'Diagnostic messages cleared'})
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route('/api/camera/snapshot')
def camera_snapshot():
    """Get a snapshot from the camera"""
    try:
        # Try the Tapo snapshot URL
        snapshot_url = f"http://{CAMERA_IP}/stream/snapshot.jpg"

        # Try to get snapshot without authentication first
        response = requests.get(snapshot_url, timeout=5)

        if response.status_code == 200:
            return Response(response.content, mimetype='image/jpeg')
        else:
            # If that fails, return a placeholder image
            return jsonify({"error": "Camera not accessible"}), 404

    except Exception as e:
        print(f"Camera error: {e}")
        return jsonify({"error": "Camera connection failed"}), 500

@app.route('/api/camera/stream')
def camera_stream():
    """Proxy camera MJPEG stream"""
    try:
        # Common MJPEG stream URLs for Tapo cameras
        possible_urls = [
            f"http://{CAMERA_IP}/stream/1",  # Tapo direct stream
            f"http://{CAMERA_IP}/videostream.cgi?resolution=8&framerate=15",  # Alternative format
            f"http://{CAMERA_IP}/video.cgi",  # Basic video stream
            f"http://{CAMERA_IP}:80/onvif/snapshot",  # ONVIF format
        ]

        for stream_url in possible_urls:
            try:
                print(f"Trying camera stream URL: {stream_url}")
                response = requests.get(stream_url, stream=True, timeout=10)
                if response.status_code == 200:
                    print(f"Success with URL: {stream_url}")
                    def generate():
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                yield chunk

                    return Response(generate(),
                                  mimetype='multipart/x-mixed-replace; boundary=frame')
            except Exception as e:
                print(f"Failed {stream_url}: {e}")
                continue

        # If all stream URLs fail, fall back to snapshot-based "stream"
        print("All stream URLs failed, falling back to snapshot stream")
        return snapshot_stream()

    except Exception as e:
        print(f"Camera stream error: {e}")
        return jsonify({"error": "Camera stream failed"}), 500

def snapshot_stream():
    """Create a pseudo-stream using snapshots if live stream isn't available"""
    import time

    def generate():
        while True:
            try:
                snapshot_url = f"http://{CAMERA_IP}/stream/snapshot.jpg"
                response = requests.get(snapshot_url, timeout=5)
                if response.status_code == 200:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + response.content + b'\r\n')
                else:
                    time.sleep(1)  # Wait before retrying
            except Exception:
                time.sleep(2)  # Wait longer on error

    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Check if we should run on port 5000 (development mode)
    import sys
    port = 5000 if '--port5000' in sys.argv else 80

    print("Starting chicken gate web interface...")
    if port == 80:
        print("Running on port 80 (default) - web interface will be available at:")
        print("  http://chicken-gate (if using Tailscale MagicDNS)")
        print("  http://YOUR_PI_IP")
        print("  http://localhost (if running locally)")
        print("")
        print("NOTE: Running on port 80 requires sudo privileges!")
        print("If you get a permission error, run with: sudo python3 web_app.py")
        print("For development mode (port 5000), use: python3 web_app.py --port5000")
    else:
        print(f"Running on port {port} (development mode) - web interface will be available at:")
        print(f"  http://chicken-gate:{port} (if using Tailscale MagicDNS)")
        print(f"  http://YOUR_PI_IP:{port}")
        print(f"  http://localhost:{port} (if running locally)")

    app.run(host='0.0.0.0', port=port, debug=True if port == 5000 else False)
