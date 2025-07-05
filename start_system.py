#!/usr/bin/env python3
"""
Startup script for the chicken gate system with web interface.
This script starts both the main gate control process and the web server.
"""

import subprocess
import sys
import os
import signal
import time

def start_gate_process():
    """Start the main gate control process"""
    print("Starting gate control process...")
    return subprocess.Popen([
        sys.executable,
        os.path.join('src', 'main.py')
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def start_web_server():
    """Start the web server"""
    print("Starting web server...")
    return subprocess.Popen([
        sys.executable,
        'web_app.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nShutting down chicken gate system...")
    global gate_process, web_process

    if gate_process:
        gate_process.terminate()
    if web_process:
        web_process.terminate()

    sys.exit(0)

def check_process_output():
    """Check for any error output from processes"""
    global gate_process, web_process

    if gate_process and gate_process.poll() is not None:
        # Gate process has stopped
        stdout, _ = gate_process.communicate()
        if stdout:
            print("❌ Gate process output:")
            print(stdout)
        return "gate"

    if web_process and web_process.poll() is not None:
        # Web process has stopped
        stdout, _ = web_process.communicate()
        if stdout:
            print("❌ Web server output:")
            print(stdout)
        return "web"

    return None

def main():
    global gate_process, web_process

    print("🐔 Starting Chicken Gate Control System")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('src/main.py'):
        print("Error: Please run this script from the chicken-gate directory")
        sys.exit(1)

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start processes
    gate_process = start_gate_process()
    time.sleep(2)  # Give gate process time to start
    web_process = start_web_server()

    print("\n✅ System started successfully!")
    print("📱 Web interface: http://localhost:5000")
    print("🔧 Gate control: Running in background")
    print("\nPress Ctrl+C to stop the system")
    print("=" * 50)

    try:
        # Monitor processes
        while True:
            failed_process = check_process_output()
            if failed_process:
                print(f"❌ {failed_process.title()} process stopped unexpectedly")
                break

            time.sleep(5)

    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

    # Cleanup
    if gate_process:
        gate_process.terminate()
    if web_process:
        web_process.terminate()

if __name__ == "__main__":
    gate_process = None
    web_process = None
    main()
