#!/bin/bash

echo "🌐 Installing Chicken Gate Web Interface Service"
echo "=============================================="

# Copy service file to systemd
echo "📋 Installing service file..."
sudo cp ./chicken-gate-web.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "✅ Enabling chicken-gate-web service..."
sudo systemctl enable chicken-gate-web.service

# Start the service
echo "🚀 Starting chicken-gate-web service..."
sudo systemctl start chicken-gate-web.service

# Show status
echo ""
echo "📊 Service Status:"
sudo systemctl status chicken-gate-web.service --no-pager

echo ""
echo "✅ Installation complete!"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status chicken-gate-web     # Check status"
echo "   sudo systemctl restart chicken-gate-web    # Restart web server"
echo "   sudo systemctl stop chicken-gate-web       # Stop web server"
echo "   sudo systemctl start chicken-gate-web      # Start web server"
echo "   sudo journalctl -u chicken-gate-web -f     # View logs"
echo ""
echo "🌐 Web interface should be available at:"
echo "   http://localhost:5000"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
