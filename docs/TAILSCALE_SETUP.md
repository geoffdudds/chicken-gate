# Tailscale MagicDNS Setup Guide

This guide will help you set up Tailscale with MagicDNS so you can access your chicken gate at `http://chicken-gate` and SSH at `ssh chicken-pi` from anywhere securely.

## What is Tailscale MagicDNS?

- **Always-on VPN** that creates a private network between your devices
- **Automatic hostnames** - no need to remember IP addresses
- **Free tier** covers your needs (up to 3 users, 100 devices)
- **Works anywhere** - home, work, mobile data
- **Zero configuration** - no port forwarding or router setup needed

## Step 1: Install Tailscale on Raspberry Pi

```bash
# Download and install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale and authenticate
sudo tailscale up

# Follow the link to authenticate in your browser
```

## Step 2: Install Tailscale on Your Devices

### Windows

1. Download from: https://tailscale.com/download/windows
2. Install and sign in with the same account

### Android/iPhone

1. Install "Tailscale" from app store
2. Sign in with the same account

### Other Devices

- Download from: https://tailscale.com/download

## Step 3: Set Up MagicDNS Hostnames

1. **Go to Tailscale Admin Console**: https://login.tailscale.com/admin/machines

2. **Find Your Raspberry Pi** in the machines list

3. **Set Machine Name**:

   - Click the "..." menu next to your Pi
   - Select "Edit machine name"
   - Set name to: `chicken-gate`

4. **Enable MagicDNS** (if not already enabled):
   - Go to "DNS" tab in admin console
   - Enable "MagicDNS"
   - Enable "HTTPS certificates" (optional, for https://chicken-gate)

## Step 4: Optional - Add Multiple Hostnames

If you want both `chicken-gate` and `chicken-pi`:

1. **In Admin Console** → **DNS** → **Nameservers**
2. **Add Custom Hosts**:
   ```
   chicken-gate    [YOUR_PI_TAILSCALE_IP]
   chicken-pi      [YOUR_PI_TAILSCALE_IP]
   ```

Or just use the machine name for both:

- Web: `http://chicken-gate`
- SSH: `ssh pi@chicken-gate`

## Step 5: Set Up the Web Service

### Option A: Run Manually (Testing)

```bash
# On your Raspberry Pi:
cd /path/to/chicken-gate
sudo python3 web_app.py
```

### Option B: Install as System Service (Recommended)

```bash
# Copy the service file
sudo cp chicken-gate-web-port80.service /etc/systemd/system/

# Edit the paths if your installation is not in /home/pi/chicken-gate
sudo nano /etc/systemd/system/chicken-gate-web-port80.service

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable chicken-gate-web-port80.service
sudo systemctl start chicken-gate-web-port80.service

# Check status
sudo systemctl status chicken-gate-web-port80.service
```

## Step 6: Test Your Setup

From any device on your Tailscale network:

### Web Interface

- Open browser to: `http://chicken-gate`
- Should show your chicken gate control panel

### SSH Access

```bash
ssh pi@chicken-gate
```

## Troubleshooting

### Can't Access http://chicken-gate

1. **Check Tailscale is running on Pi**: `sudo tailscale status`
2. **Check web service is running**: `sudo systemctl status chicken-gate-web-port80`
3. **Check MagicDNS is enabled** in Tailscale admin console
4. **Try direct IP**: `http://100.x.x.x` (Tailscale IP shown in admin console)

### Permission Denied on Port 80

```bash
# Make sure you're running with sudo
sudo python3 web_app.py

# Or for development mode (port 5000, no sudo needed)
python3 web_app.py --port5000
# Then access at: http://chicken-gate:5000
```

### SSH Not Working

```bash
# Make sure SSH is enabled on Pi
sudo systemctl enable ssh
sudo systemctl start ssh

# Try with username
ssh pi@chicken-gate
```

## Final Result

Once set up, you'll have:

✅ **Web Interface**: `http://chicken-gate` (from anywhere)
✅ **SSH Access**: `ssh pi@chicken-gate` (from anywhere)
✅ **Secure**: No ports open to internet, works through Tailscale VPN
✅ **Easy**: No IP addresses to remember
✅ **Mobile-friendly**: Bookmark `http://chicken-gate` on your phone

## Family Sharing

- **One Tailscale account** can be shared by family members
- **Each person installs** Tailscale app on their devices
- **Everyone signs in** with the same account
- **Everyone gets access** to `http://chicken-gate`

Perfect for a family chicken gate system!
