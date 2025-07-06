#!/usr/bin/env python3
"""
Install dependencies for RTSP camera support
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    print("Installing RTSP camera dependencies...")
    print("="*40)

    # Required packages for RTSP support
    packages = [
        "opencv-python",  # For RTSP stream handling
        "pillow",         # For image processing (if not already installed)
    ]

    success_count = 0
    for package in packages:
        print(f"\nInstalling {package}...")
        if install_package(package):
            success_count += 1

    print("\n" + "="*40)
    print(f"Installation complete: {success_count}/{len(packages)} packages installed")

    if success_count == len(packages):
        print("✓ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Run: python test_rtsp.py")
        print("2. Test RTSP streams with VLC or the generated OpenCV script")
        print("3. Update web application with working RTSP integration")
    else:
        print("✗ Some packages failed to install")
        print("Try running: pip install opencv-python pillow")

if __name__ == "__main__":
    main()
