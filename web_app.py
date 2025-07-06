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
CAMERA_USERNAME = "admin"  # Try admin as default username for Tapo
CAMERA_PASSWORD = "admin"  # Try admin as default password

# Common ports for IP cameras (focus on working ones from your test)
CAMERA_PORTS = [554, 443, 8443, 80, 8080, 88, 1935]

# RTSP stream URLs for Tapo cameras
RTSP_URLS = [
    f"rtsp://{CAMERA_IP}:554/stream1",
    f"rtsp://{CAMERA_IP}:554/stream2",
    f"rtsp://{CAMERA_IP}:554/live",
    f"rtsp://{CAMERA_IP}:554/Streaming/Channels/101",
    f"rtsp://{CAMERA_IP}:554/Streaming/Channels/1",
]

# Since Tapo cameras often don't support direct HTTP access, we'll create a mock camera feed
# You can replace this with actual camera integration once you set up proper credentials

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
    """Get a snapshot from the camera or return a placeholder"""
    try:
        # TP-Link Tapo cameras typically don't support direct HTTP snapshot access
        # They usually require the Tapo app or ONVIF/RTSP protocols with proper authentication

        # Try a few HTTP snapshot URLs just in case
        test_urls = [
            f"http://{CAMERA_IP}/tmpfs/auto.jpg",
            f"http://{CAMERA_IP}/jpg/image.jpg",
            f"http://{CAMERA_IP}/snapshot.jpg",
        ]

        for url in test_urls:
            try:
                print(f"Trying snapshot URL: {url}")
                response = requests.get(url, timeout=3,
                                      auth=(CAMERA_USERNAME, CAMERA_PASSWORD))
                if response.status_code == 200 and len(response.content) > 1000:
                    print(f"Success with snapshot URL: {url}")
                    return Response(response.content, mimetype='image/jpeg')
            except Exception as e:
                if "Connection refused" not in str(e):
                    print(f"Failed {url}: {e}")
                continue

        # Return a placeholder image with camera info instead of an error
        return create_placeholder_image()

    except Exception as e:
        print(f"Camera error: {e}")
        return create_placeholder_image()

def create_placeholder_image():
    """Create a placeholder image when camera is not accessible via HTTP"""
    import io
    from PIL import Image, ImageDraw, ImageFont

    try:
        # Create a simple placeholder image
        img = Image.new('RGB', (640, 480))
        img.paste((44, 62, 80), [0, 0, 640, 480])  # Fill with dark blue-gray color
        draw = ImageDraw.Draw(img)

        # Try to use a default font, fall back to basic if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Draw text
        text1 = "📷 TP-Link Tapo Camera"
        text2 = f"IP: {CAMERA_IP}"
        text3 = "Camera requires Tapo app"
        text4 = "or RTSP/ONVIF protocol"
        text5 = "for live streaming"

        # Get text size and center it
        bbox1 = draw.textbbox((0, 0), text1, font=font)
        bbox2 = draw.textbbox((0, 0), text2, font=small_font)
        bbox3 = draw.textbbox((0, 0), text3, font=small_font)
        bbox4 = draw.textbbox((0, 0), text4, font=small_font)
        bbox5 = draw.textbbox((0, 0), text5, font=small_font)

        x1 = (640 - (bbox1[2] - bbox1[0])) // 2
        x2 = (640 - (bbox2[2] - bbox2[0])) // 2
        x3 = (640 - (bbox3[2] - bbox3[0])) // 2
        x4 = (640 - (bbox4[2] - bbox4[0])) // 2
        x5 = (640 - (bbox5[2] - bbox5[0])) // 2

        draw.text((x1, 180), text1, fill='white', font=font)
        draw.text((x2, 220), text2, fill=(189, 195, 199), font=small_font)  # Light gray
        draw.text((x3, 260), text3, fill=(189, 195, 199), font=small_font)
        draw.text((x4, 280), text4, fill=(189, 195, 199), font=small_font)
        draw.text((x5, 300), text5, fill=(189, 195, 199), font=small_font)

        # Save to bytes
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=85)
        img_io.seek(0)

        return Response(img_io.getvalue(), mimetype='image/jpeg')

    except ImportError:
        # If PIL is not available, return a simple text response
        return Response("Camera not accessible via HTTP - Tapo cameras require special protocols",
                       mimetype='text/plain')

@app.route('/api/camera/stream')
def camera_stream():
    """Proxy camera MJPEG stream or fall back to snapshot stream"""
    try:
        # TP-Link Tapo cameras typically don't support direct MJPEG streaming without authentication
        # Most require the Tapo app or RTSP/ONVIF protocols
        print("Tapo cameras typically require RTSP or Tapo app for streaming")
        print("Falling back to placeholder image stream")
        return placeholder_stream()

    except Exception as e:
        print(f"Camera stream error: {e}")
        return placeholder_stream()

def placeholder_stream():
    """Create a stream showing placeholder images"""
    import time

    def generate():
        while True:
            try:
                # Get the placeholder image as bytes
                placeholder_response = create_placeholder_image()
                if hasattr(placeholder_response, 'data'):
                    image_data = placeholder_response.data
                else:
                    image_data = placeholder_response.get_data()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image_data + b'\r\n')

                # Update every 5 seconds (slower for placeholder)
                time.sleep(5)

            except Exception as e:
                print(f"Placeholder stream error: {e}")
                time.sleep(5)

    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# Removed old snapshot_stream function - replaced with placeholder_stream

@app.route('/api/camera/debug')
def camera_debug():
    """Debug endpoint to test camera connectivity"""
    try:
        debug_info = {
            "camera_ip": CAMERA_IP,
            "timestamp": datetime.now().isoformat(),
            "camera_type": "TP-Link Tapo C320WS",
            "ports_tested": CAMERA_PORTS,
            "rtsp_urls": RTSP_URLS,
            "notes": [
                "TP-Link Tapo cameras typically require:",
                "1. Tapo mobile app for setup and viewing",
                "2. RTSP protocol for streaming (port 554)",
                "3. ONVIF protocol for integration",
                "4. Proper authentication credentials",
                "Direct HTTP snapshot access is usually not supported"
            ],
            "tests": []
        }

        # Test basic connectivity to key ports
        key_ports = [554, 443, 8443]  # Focus on ports that showed activity
        for port in key_ports:
            basic_url = f"http://{CAMERA_IP}:{port}"
            test_result = {
                "url": basic_url,
                "port": port,
                "type": "basic_connectivity",
                "status": "unknown",
                "response_code": None,
                "content_type": None,
                "content_size": 0,
                "error": None,
                "notes": ""
            }

            if port == 554:
                test_result["notes"] = "RTSP port - requires RTSP client"
            elif port == 443:
                test_result["notes"] = "HTTPS port - may require web login"
            elif port == 8443:
                test_result["notes"] = "Alternative HTTPS port"

            try:
                response = requests.get(basic_url, timeout=3)
                test_result["status"] = "success" if response.status_code == 200 else "failed"
                test_result["response_code"] = response.status_code
                test_result["content_type"] = response.headers.get('content-type', 'unknown')
                test_result["content_size"] = len(response.content)
            except Exception as e:
                test_result["status"] = "error"
                test_result["error"] = str(e)

            debug_info["tests"].append(test_result)

        # Add RTSP connection test info (we can't actually test RTSP with requests)
        rtsp_info = {
            "type": "rtsp_info",
            "status": "info",
            "notes": "RTSP testing requires specialized tools like ffmpeg or VLC",
            "suggested_rtsp_urls": RTSP_URLS,
            "test_command": f"ffplay -rtsp_transport tcp rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/stream1"
        }
        debug_info["tests"].append(rtsp_info)

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
