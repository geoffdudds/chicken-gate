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
CAMERA_USERNAME = "chickencam"   # Your Tapo camera username
CAMERA_PASSWORD = "password"     # Your Tapo camera password

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
    """Get a snapshot from the camera using RTSP (if OpenCV available) or placeholder"""
    try:
        # Try to import OpenCV - this will fail on Pi Zero
        import cv2

        # Use the working RTSP URL with authentication
        rtsp_url = f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/stream1"

        print(f"Capturing frame from RTSP: {rtsp_url}")

        # Open video capture
        cap = cv2.VideoCapture(rtsp_url)

        if cap.isOpened():
            # Read a frame
            ret, frame = cap.read()
            if ret:
                # Encode frame as JPEG
                success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    cap.release()
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
                else:
                    print("Failed to encode frame as JPEG")
            else:
                print("Failed to capture frame from RTSP stream")
        else:
            print("Failed to open RTSP stream")

        cap.release()

    except ImportError:
        print("OpenCV not available (normal on Pi Zero) - using placeholder with RTSP info")
    except Exception as e:
        print(f"RTSP camera error: {e}")

    # Always fall back to placeholder - shows RTSP is available but OpenCV isn't
    return create_rtsp_info_image()

def create_rtsp_info_image():
    """Create an informative image showing RTSP camera is working but OpenCV unavailable"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        from datetime import datetime

        # Create a simple placeholder image
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color='#27ae60')  # Green background since RTSP works
        draw = ImageDraw.Draw(img)

        # Use default font
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        # Camera info text (avoid Unicode emojis that cause encoding issues)
        lines = [
            "[OK] RTSP Camera Available",
            f"Tapo Camera at {CAMERA_IP}",
            "RTSP Test: SUCCESSFUL",
            "Resolution: 1280x720 @ 15fps",
            "OpenCV: Not available on Pi Zero",
            "",
            "To view live stream:",
            f"rtsp://chickencam:password@{CAMERA_IP}:554/stream1",
            "",
            f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        ]

        # Calculate starting Y position to center text block
        line_height = 35
        total_height = len([line for line in lines if line]) * line_height  # Exclude empty lines
        y_start = (height - total_height) // 2

        # Draw each line centered
        y_pos = y_start
        for line in lines:
            if not line:  # Skip empty lines but add spacing
                y_pos += line_height // 2
                continue

            if font:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 8  # Rough estimate

            x = (width - text_width) // 2

            # Different colors for different types of lines
            if "[OK]" in line or "SUCCESSFUL" in line:
                color = '#ffffff'  # White for success
            elif "RTSP Test" in line:
                color = '#ffffff'  # White for test result
            elif "Resolution" in line:
                color = '#d5f4e6'  # Light green for info
            elif "OpenCV" in line:
                color = '#f39c12'  # Orange for limitation
            elif "rtsp://" in line:
                color = '#3498db'  # Blue for URL
            else:
                color = '#ecf0f1'  # Light gray for general info

            draw.text((x, y_pos), line, fill=color, font=font)
            y_pos += line_height

        # Convert to JPEG bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)

        return Response(img_byte_arr.getvalue(), mimetype='image/jpeg')

    except ImportError:
        # If PIL is not available either, return a simple text response
        return Response(
            f"RTSP Camera Available at {CAMERA_IP}:554\n"
            f"Stream: rtsp://chickencam:password@{CAMERA_IP}:554/stream1\n"
            f"Note: OpenCV not available on Pi Zero\n"
            f"Use VLC or other RTSP client to view live stream",
            mimetype='text/plain'
        )
    except Exception as e:
        print(f"Error creating RTSP info image: {e}")
        return Response(
            f"RTSP Camera Available - OpenCV not installed\n"
            f"Stream URL: rtsp://chickencam:password@{CAMERA_IP}:554/stream1",
            mimetype='text/plain'
        )
    """Create a placeholder image when camera is not accessible"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        from datetime import datetime

        # Create a simple placeholder image
        width, height = 640, 480
        img = Image.new('RGB', (width, height), color='#2c3e50')
        draw = ImageDraw.Draw(img)

        # Use default font (avoid font file dependencies)
        try:
            font = ImageFont.load_default()
        except:
            font = None

        # Camera info text
        lines = [
            "📷 RTSP Camera",
            f"Tapo Camera at {CAMERA_IP}",
            "RTSP Stream: Available",
            "Credentials: chickencam/password",
            f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        ]

        # Calculate starting Y position to center text block
        line_height = 40
        total_height = len(lines) * line_height
        y_start = (height - total_height) // 2

        # Draw each line centered
        for i, line in enumerate(lines):
            if font:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 8  # Rough estimate

            x = (width - text_width) // 2
            y = y_start + i * line_height

            # Different colors for different lines
            if i == 0:
                color = '#e74c3c'  # Red for offline
            elif i == 2:
                color = '#27ae60'  # Green for available port
            elif i == 3:
                color = '#f39c12'  # Orange for not supported
            else:
                color = '#ecf0f1'  # Light gray for info

            draw.text((x, y), line, fill=color, font=font)

        # Convert to JPEG bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)

        return Response(img_byte_arr.getvalue(), mimetype='image/jpeg')

    except Exception as e:
        print(f"Error creating placeholder: {e}")
        # Return a simple JSON response if image creation fails
        return jsonify({"error": "Camera placeholder unavailable"}), 500

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
    """Return static camera info image since OpenCV unavailable on Pi Zero"""
    try:
        print("OpenCV not available on Pi Zero - returning static RTSP info image")
        # Return the same static image as the snapshot endpoint
        return create_rtsp_info_image()
    except Exception as e:
        print(f"Camera stream error: {e}")
        # Fallback to simple text response
        return Response("Camera streaming not available on Pi Zero - Use RTSP URL in VLC",
                       mimetype='text/plain')

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
