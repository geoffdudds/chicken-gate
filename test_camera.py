#!/usr/bin/env python3
"""
Simple camera connectivity test script
Run this to test what works with your TP-Link Tapo camera
"""

import requests
import socket
from datetime import datetime

CAMERA_IP = "192.168.0.135"

def test_basic_connectivity():
    """Test if camera responds to ping and basic network connectivity"""
    print("=" * 50)
    print("BASIC CONNECTIVITY TEST")
    print("=" * 50)
    
    # Test if we can reach the camera IP
    try:
        # Simple socket test
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Test common ports
        ports = [80, 8080, 443, 554, 88, 8443, 1935]
        for port in ports:
            try:
                result = sock.connect_ex((CAMERA_IP, port))
                if result == 0:
                    print(f"✓ Port {port}: OPEN")
                else:
                    print(f"✗ Port {port}: CLOSED")
            except Exception as e:
                print(f"✗ Port {port}: ERROR - {e}")
            finally:
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
        sock.close()
    except Exception as e:
        print(f"Network test failed: {e}")

def test_http_endpoints():
    """Test HTTP endpoints that might work"""
    print("\n" + "=" * 50)
    print("HTTP ENDPOINTS TEST")
    print("=" * 50)
    
    # Common HTTP URLs for IP cameras
    test_urls = [
        f"http://{CAMERA_IP}",
        f"http://{CAMERA_IP}:80",
        f"http://{CAMERA_IP}:8080",
        f"http://{CAMERA_IP}/",
        f"http://{CAMERA_IP}/snapshot.jpg",
        f"http://{CAMERA_IP}/image.jpg", 
        f"http://{CAMERA_IP}/tmpfs/auto.jpg",
        f"http://{CAMERA_IP}/cgi-bin/snapshot.cgi",
        f"http://{CAMERA_IP}/snapshot.cgi",
        f"http://{CAMERA_IP}/stream/snapshot.jpg",
        f"http://{CAMERA_IP}/jpg/image.jpg",
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=5)
            print(f"  ✓ Status: {response.status_code}")
            print(f"  ✓ Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  ✓ Size: {len(response.content)} bytes")
            
            # If it looks like an image, save it for inspection
            if 'image' in response.headers.get('content-type', '').lower() and len(response.content) > 1000:
                filename = f"camera_test_{datetime.now().strftime('%H%M%S')}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ Saved image to: {filename}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection refused")
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()

def test_with_auth():
    """Test with common username/password combinations"""
    print("\n" + "=" * 50)
    print("AUTHENTICATION TEST")
    print("=" * 50)
    
    # Common credentials for IP cameras
    credentials = [
        ("admin", "admin"),
        ("admin", "password"),
        ("admin", ""),
        ("root", "root"),
        ("user", "user"),
        ("", ""),
    ]
    
    test_url = f"http://{CAMERA_IP}"
    
    for username, password in credentials:
        try:
            print(f"Testing credentials: {username}:{password}")
            if username or password:
                response = requests.get(test_url, auth=(username, password), timeout=5)
            else:
                response = requests.get(test_url, timeout=5)
            
            print(f"  ✓ Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ SUCCESS! Working credentials found")
                print(f"  ✓ Content-Type: {response.headers.get('content-type', 'unknown')}")
                break
            elif response.status_code == 401:
                print(f"  ✗ Unauthorized (wrong credentials)")
            else:
                print(f"  ? Unexpected status code")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection refused")
            break  # No point trying other credentials if we can't connect
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()

def test_camera_web_interface():
    """Try to access the camera's web interface"""
    print("\n" + "=" * 50)
    print("WEB INTERFACE TEST")
    print("=" * 50)
    
    # Try to access the camera's main web page
    try:
        print(f"Trying to access camera web interface at http://{CAMERA_IP}")
        response = requests.get(f"http://{CAMERA_IP}", timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Server: {response.headers.get('server', 'unknown')}")
        print(f"Content length: {len(response.content)} bytes")
        
        # Save the response for inspection
        with open("camera_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✓ Response saved to camera_response.html")
        
        # Look for common camera interface indicators
        content = response.text.lower()
        if "tapo" in content:
            print("✓ Found 'Tapo' in response - this is likely a Tapo camera interface")
        if "login" in content:
            print("✓ Found 'login' in response - camera requires authentication")
        if "streaming" in content or "stream" in content:
            print("✓ Found streaming references in response")
            
    except Exception as e:
        print(f"✗ Error accessing web interface: {e}")

if __name__ == "__main__":
    print(f"Testing TP-Link Tapo Camera at {CAMERA_IP}")
    print(f"Test started at: {datetime.now()}")
    
    test_basic_connectivity()
    test_http_endpoints()
    test_with_auth()
    test_camera_web_interface()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print("Check the output above for working endpoints.")
    print("If any images were downloaded, check them to see if they're valid camera feeds.")
