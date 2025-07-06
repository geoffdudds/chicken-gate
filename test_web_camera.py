#!/usr/bin/env python3
"""
Test the camera functions directly from web_app.py to debug the issue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from web_app import create_rtsp_info_image
    print("✅ Successfully imported create_rtsp_info_image")

    print("Testing create_rtsp_info_image()...")
    result = create_rtsp_info_image()

    print(f"Result type: {type(result)}")
    print(f"Result: {result}")

    if hasattr(result, 'mimetype'):
        print(f"MIME type: {result.mimetype}")
    if hasattr(result, 'data'):
        print(f"Data length: {len(result.data)} bytes")
    elif hasattr(result, 'response'):
        print(f"Response length: {len(result.response)} bytes")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
