# Camera Setup for Pi Zero - README

## Overview

Due to hardware limitations on the Raspberry Pi Zero, the chicken gate system uses a lightweight camera integration approach that doesn't require OpenCV (which cannot be installed on Pi Zero due to memory constraints).

## Camera Integration Status

### ✅ What Works on Pi Zero:

- **Static camera snapshots** - Shows RTSP connection info and instructions
- **Camera debugging** - Connectivity tests and port scanning
- **RTSP URL copying** - Easy access to live stream URLs for external apps
- **Camera controls** - Web interface buttons for camera management

### ❌ What Doesn't Work on Pi Zero:

- **Live streaming in web browser** - Requires OpenCV for video processing
- **MJPEG streaming** - TP-Link Tapo cameras don't support HTTP/MJPEG
- **Direct HTTP camera access** - Tapo cameras use proprietary protocols

## How to View Live Camera Feed

### Method 1: VLC Media Player (Recommended)

1. Open VLC on your computer/phone
2. Go to **Media > Open Network Stream**
3. Enter: `rtsp://chickencam:password@192.168.0.135:554/stream1`
4. Click **Play**

### Method 2: Mobile Apps

- **Android**: VLC for Android, RTSP Player, IP Cam Viewer
- **iOS**: VLC for iOS, RTSP Player, Live Cams Pro
- Use the same RTSP URL: `rtsp://chickencam:password@192.168.0.135:554/stream1`

### Method 3: Web Interface Helper

1. Go to your chicken gate web interface
2. Click **"📋 Copy RTSP URL"** button
3. The URL will be copied to clipboard with instructions
4. Paste into your preferred RTSP app

## Technical Details

### Camera: TP-Link Tapo C320WS

- **IP Address**: 192.168.0.135
- **Username**: chickencam
- **Password**: password
- **RTSP Port**: 554
- **Protocol**: RTSP only (no HTTP/MJPEG support)

### RTSP Stream URLs (try in order):

1. `rtsp://chickencam:password@192.168.0.135:554/stream1` (main quality)
2. `rtsp://chickencam:password@192.168.0.135:554/stream2` (sub quality)
3. `rtsp://chickencam:password@192.168.0.135:554/live`

### Web Interface Endpoints:

- `/api/camera/snapshot` - Returns static info image with RTSP details
- `/api/camera/stream` - Returns same static image (no streaming on Pi Zero)
- `/api/camera/debug` - Camera connectivity and diagnostic information

## Troubleshooting

### Camera Not Accessible:

1. Check camera power and WiFi connection
2. Verify IP address hasn't changed: `nmap -sn 192.168.0.0/24`
3. Test RTSP connection: Use VLC to verify stream works
4. Check credentials: Ensure username/password are correct

### RTSP Stream Issues:

1. **Authentication Error**: Verify credentials in Tapo app
2. **Connection Timeout**: Check network connectivity to camera
3. **Stream Not Found**: Try different RTSP URLs listed above
4. **Codec Issues**: Use VLC which supports most formats

### Web Interface Issues:

1. **Blank Camera Section**: Check Flask app logs for errors
2. **Stream Hanging**: Fixed in latest update - should show static image
3. **Copy Button Not Working**: Browser clipboard permissions required

## Future Improvements

If you upgrade to a more powerful Pi (Pi 4, Pi 5), you could:

- Install OpenCV for live web streaming
- Implement RTSP-to-MJPEG proxy
- Add motion detection features
- Support multiple camera feeds

For now, the Pi Zero setup provides reliable gate control with camera monitoring via external RTSP apps.

## File Locations

- **Web App**: `web_app.py` - Flask server with camera endpoints
- **HTML Interface**: `templates/index.html` - Web UI with camera controls
- **Test Scripts**: `test_*.py` - Camera connectivity testing
- **This Guide**: `CAMERA_SETUP_PI_ZERO.md`
