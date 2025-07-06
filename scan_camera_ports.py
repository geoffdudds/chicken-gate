#!/usr/bin/env python3
"""
Simple port scanner for the camera
"""

import socket
import sys

CAMERA_IP = "192.168.0.135"

def scan_port(ip, port, timeout=3):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

print(f"Scanning {CAMERA_IP} for open ports...")
print("-" * 40)

# Common camera ports
ports = [21, 22, 23, 53, 80, 88, 443, 554, 1935, 8080, 8443, 9999]

open_ports = []
for port in ports:
    if scan_port(CAMERA_IP, port):
        print(f"Port {port}: OPEN")
        open_ports.append(port)
    else:
        print(f"Port {port}: closed")

print("-" * 40)
if open_ports:
    print(f"Open ports found: {open_ports}")
    print("\nCommon port uses:")
    for port in open_ports:
        if port == 80:
            print(f"  {port}: HTTP web interface")
        elif port == 443:
            print(f"  {port}: HTTPS web interface")
        elif port == 554:
            print(f"  {port}: RTSP streaming")
        elif port == 8080:
            print(f"  {port}: Alternative HTTP")
        elif port == 22:
            print(f"  {port}: SSH")
        elif port == 23:
            print(f"  {port}: Telnet")
        else:
            print(f"  {port}: Unknown service")
else:
    print("No open ports found - camera may be offline or heavily firewalled")
