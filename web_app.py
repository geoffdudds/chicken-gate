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
        # Try different snapshot URLs for TP-Link Tapo cameras
        possible_urls = [
            f"http://{CAMERA_IP}/stream/snapshot.jpg",  # Generic snapshot
            f"http://{CAMERA_IP}/tmpfs/auto.jpg",       # Tapo internal snapshot
            f"http://{CAMERA_IP}/snapshot.cgi",         # CGI-based snapshot
            f"http://{CAMERA_IP}/image/jpeg.cgi",       # Alternative format
        ]

        for snapshot_url in possible_urls:
            try:
                print(f"Trying snapshot URL: {snapshot_url}")
                response = requests.get(snapshot_url, timeout=10,
                                      auth=(CAMERA_USERNAME, CAMERA_PASSWORD) if CAMERA_USERNAME != "chickencam" else None)
                if response.status_code == 200 and len(response.content) > 1000:  # Basic check for valid image
                    print(f"Success with snapshot URL: {snapshot_url}")
                    return Response(response.content, mimetype='image/jpeg')
            except Exception as e:
                print(f"Failed snapshot URL {snapshot_url}: {e}")
                continue

        return jsonify({"error": "Camera not accessible"}), 404

    except Exception as e:
        print(f"Camera error: {e}")
        return jsonify({"error": "Camera connection failed"}), 500

@app.route('/api/camera/stream')
def camera_stream():
    """Proxy camera MJPEG stream or fall back to snapshot stream"""
    try:
        # TP-Link Tapo cameras typically don't support direct MJPEG streaming without authentication
        # Let's try a few common URLs but expect to fall back to snapshot streaming
        possible_urls = [
            f"http://{CAMERA_IP}/stream/1",  # Generic stream endpoint
            f"http://{CAMERA_IP}/video.mjpg",  # Common MJPEG endpoint
            f"http://{CAMERA_IP}/mjpeg/1",  # Alternative MJPEG
            f"http://{CAMERA_IP}/cgi-bin/mjpg/video.cgi",  # CGI-based stream
        ]

        for stream_url in possible_urls:
            try:
                print(f"Trying camera stream URL: {stream_url}")
                response = requests.get(stream_url, stream=True, timeout=5,
                                      auth=(CAMERA_USERNAME, CAMERA_PASSWORD) if CAMERA_USERNAME != "chickencam" else None)
                if response.status_code == 200 and 'image' in response.headers.get('content-type', '').lower():
                    print(f"Success with MJPEG URL: {stream_url}")
                    def generate():
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                yield chunk

                    return Response(generate(),
                                  mimetype='multipart/x-mixed-replace; boundary=frame')
            except Exception as e:
                print(f"Failed {stream_url}: {e}")
                continue

        # Most Tapo cameras require their mobile app or special protocols
        # Fall back to snapshot-based "stream" which works more reliably
        print("No direct MJPEG stream available, using snapshot-based stream")
        return snapshot_stream()

    except Exception as e:
        print(f"Camera stream error: {e}")
        return snapshot_stream()  # Always fall back to snapshot stream

def snapshot_stream():
    """Create a pseudo-stream using snapshots if live stream isn't available"""
    import time

    def generate():
        while True:
            try:
                # Try the same snapshot URLs as the snapshot endpoint
                possible_urls = [
                    f"http://{CAMERA_IP}/stream/snapshot.jpg",
                    f"http://{CAMERA_IP}/tmpfs/auto.jpg",
                    f"http://{CAMERA_IP}/snapshot.cgi",
                    f"http://{CAMERA_IP}/image/jpeg.cgi",
                ]

                success = False
                for snapshot_url in possible_urls:
                    try:
                        response = requests.get(snapshot_url, timeout=5,
                                              auth=(CAMERA_USERNAME, CAMERA_PASSWORD) if CAMERA_USERNAME != "chickencam" else None)
                        if response.status_code == 200 and len(response.content) > 1000:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + response.content + b'\r\n')
                            success = True
                            break
                    except Exception:
                        continue

                if not success:
                    # If no snapshot worked, wait longer before retrying
                    time.sleep(3)
                else:
                    # Update every 2 seconds for smooth "streaming"
                    time.sleep(2)

            except Exception as e:
                print(f"Snapshot stream error: {e}")
                time.sleep(5)  # Wait longer on error

    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/debug')
def camera_debug():
    """Debug endpoint to test camera connectivity"""
    try:
        debug_info = {
            "camera_ip": CAMERA_IP,
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }

        # Test different URLs
        test_urls = [
            f"http://{CAMERA_IP}/stream/snapshot.jpg",
            f"http://{CAMERA_IP}/tmpfs/auto.jpg",
            f"http://{CAMERA_IP}/snapshot.cgi",
            f"http://{CAMERA_IP}/image/jpeg.cgi",
            f"http://{CAMERA_IP}/stream/1",
            f"http://{CAMERA_IP}/video.mjpg",
            f"http://{CAMERA_IP}",  # Just test basic connectivity
        ]

        for url in test_urls:
            test_result = {
                "url": url,
                "status": "unknown",
                "response_code": None,
                "content_type": None,
                "content_size": 0,
                "error": None
            }

            try:
                response = requests.get(url, timeout=5)
                test_result["status"] = "success" if response.status_code == 200 else "failed"
                test_result["response_code"] = response.status_code
                test_result["content_type"] = response.headers.get('content-type', 'unknown')
                test_result["content_size"] = len(response.content)
            except Exception as e:
                test_result["status"] = "error"
                test_result["error"] = str(e)

            debug_info["tests"].append(test_result)

        return jsonify(debug_info)

    except Exception as e:
        return jsonify({"error": f"Debug failed: {e}"}), 500

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
