#!/bin/bash

echo "🔄 Updating Chicken Gate Web Interface Service"
echo "============================================="

# Copy updated service file
echo "📋 Updating service file..."
sudo cp ./chicken-gate-web.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Restart the service
echo "🚀 Restarting chicken-gate-web service..."
sudo systemctl restart chicken-gate-web.service

# Show status
echo ""
echo "📊 Service Status:"
sudo systemctl status chicken-gate-web.service --no-pager

echo ""
echo "✅ Update complete!"
echo "🌐 Web interface: http://$(hostname -I | awk '{print $1}'):5000"
