#!/bin/bash

echo "🔄 Updating Chicken Gate Web Interface Service"
echo "============================================="

# Check which service to update (default to port 5000)
if [ "$1" = "--port80" ] || [ "$1" = "--prod" ]; then
    SERVICE_NAME="chicken-gate-web-port80"
    SERVICE_FILE="chicken-gate-web-port80.service"
    PORT="80"
    URL_SUFFIX=""
    echo "📌 Updating PRODUCTION service (port 80)"
    OTHER_SERVICE="chicken-gate-web"
else
    SERVICE_NAME="chicken-gate-web"
    SERVICE_FILE="chicken-gate-web.service"
    PORT="5000"
    URL_SUFFIX=":5000"
    echo "🔧 Updating DEVELOPMENT service (port 5000)"
    OTHER_SERVICE="chicken-gate-web-port80"
fi

echo ""

# Stop and disable the other service to prevent conflicts
echo "🛑 Ensuring no service conflicts..."
sudo systemctl stop $OTHER_SERVICE 2>/dev/null || true
sudo systemctl disable $OTHER_SERVICE 2>/dev/null || true

# Kill any manually running web app processes
echo "🧹 Cleaning up manual processes..."
pkill -f "web_app.py" 2>/dev/null || true
sleep 2  # Give processes time to terminate

# Copy updated service file
echo "📋 Updating service file ($SERVICE_FILE)..."
sudo cp ./$SERVICE_FILE /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the desired service
echo "🚀 Enabling and starting $SERVICE_NAME service..."
sudo systemctl enable $SERVICE_NAME.service
sudo systemctl restart $SERVICE_NAME.service

# Show status
echo ""
echo "📊 Service Status:"
sudo systemctl status $SERVICE_NAME.service --no-pager

echo ""
echo "✅ Update complete!"

# Show access URLs
HOSTNAME=$(hostname -I | awk '{print $1}')
echo "🌐 Access URLs:"
echo "   Direct IP: http://$HOSTNAME$URL_SUFFIX"
echo "   Tailscale: http://chicken-gate$URL_SUFFIX"

if [ "$PORT" = "80" ]; then
    echo ""
    echo "💡 Clean URL with no port number! Perfect for bookmarks."
else
    echo ""
    echo "💡 Development mode - no root privileges needed."
    echo "✅ Port 5000 + Tailscale = Perfect"
    echo "   - Clean URLs: http://chicken-gate:5000"
    echo "   - Secure by default (Tailscale network)"
    echo "   - No root required"
fi

echo ""
echo "📋 To switch services:"
echo "   Development (port 5000): ./update-web-service.sh"
echo "   Production (port 80): ./update-web-service.sh --port80"