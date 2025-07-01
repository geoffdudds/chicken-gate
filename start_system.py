#!/bin/bash
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
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_web_server():
    """Start the web server"""
    print("Starting web server...")
    return subprocess.Popen([
        sys.executable,
        'web_app.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\nShutting down chicken gate system...")
    global gate_process, web_process

    if gate_process:
        gate_process.terminate()
    if web_process:
        web_process.terminate()

    sys.exit(0)

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
            # Check if processes are still running
            if gate_process.poll() is not None:
                print("❌ Gate process stopped unexpectedly")
                break

            if web_process.poll() is not None:
                print("❌ Web server stopped unexpectedly")
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
