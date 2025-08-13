# Chicken Gate Web Interface

A modern web interface to monitor and control your automated chicken gate system.

## Features

🔍 **Real-time Monitoring**

- Gate position with visual progress bar
- Closed switch status
- Open switch status (when installed)
- Live updates every 2 seconds

🎮 **Remote Control**

- Open gate button
- Close gate button
- Reset position (auto or manual)
- Command feedback and status messages

📱 **Responsive Design**

- Works on desktop, tablet, and mobile
- Modern, beautiful interface
- Easy-to-use controls

## Setup

1. **Install dependencies:**

   ```bash
   pip install flask
   ```

2. **Start the system:**

   ```bash
   python start_system.py
   ```

   This starts both the gate control process and web server.

3. **Access the web interface:**
   Open your browser to: `http://localhost:5000`

## Manual Startup

If you prefer to start components separately:

1. **Start the gate control process:**

   ```bash
   cd src
   python main.py
   ```

2. **Start the web server (in another terminal):**
   ```bash
   python web_app.py
   ```

## Commands

The web interface supports all the same commands as the command-line tool:

- **OPEN** - Open the gate
- **CLOSE** - Close the gate
- **RESET** - Reset position based on switch state
- **RESET:position** - Reset to specific position (0-100)

## Network Access

To access the web interface from other devices on your network:

1. Find your Raspberry Pi's IP address:

   ```bash
   hostname -I
   ```

2. Access from other devices:
   `http://YOUR_PI_IP:5000`

## Security Note

The web interface runs without authentication by default. If you plan to expose it to the internet, consider adding authentication or running it behind a VPN.

## Troubleshooting

**Web interface shows "Unknown" status:**

- Check that the main gate process is running
- Verify the `gate_status.json` file is being created

**Commands not working:**

- Ensure the gate control process can write to `gate_cmd.txt`
- Check file permissions in the project directory

**Can't access from other devices:**

- Check firewall settings
- Ensure port 5000 is open
- Verify the Pi's IP address

## File Structure

```
chicken-gate/
├── web_app.py              # Flask web server
├── templates/
│   └── index.html          # Web interface template
├── start_system.py         # System startup script
├── gate_status.json        # Status file (auto-generated)
├── gate_cmd.txt           # Command file (auto-generated)
└── src/
    └── main.py            # Main gate control (modified)
```
