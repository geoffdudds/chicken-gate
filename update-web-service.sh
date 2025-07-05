#!/bin/bash

echo "🔄 Updating Chicken Gate Web Interface Service"
echo "============================================="

# Check which service to update (default to port 80)
if [ "$1" = "--port5000" ] || [ "$1" = "--dev" ]; then
    SERVICE_NAME="chicken-gate-web"
    SERVICE_FILE="chicken-gate-web.service"
    PORT="5000"
    URL_SUFFIX=":5000"
    echo "� Updating DEVELOPMENT service (port 5000)"
else
    SERVICE_NAME="chicken-gate-web-port80"
    SERVICE_FILE="chicken-gate-web-port80.service"
    PORT="80"
    URL_SUFFIX=""
    echo "📌 Updating PRODUCTION service (port 80)"
fi

echo ""

# Copy updated service file
echo "📋 Updating service file ($SERVICE_FILE)..."
sudo cp ./$SERVICE_FILE /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Restart the service
echo "🚀 Restarting $SERVICE_NAME service..."
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
fi

echo ""
echo "📋 To switch services:"
echo "   Production (port 80): ./update-web-service.sh"
echo "   Development (port 5000): ./update-web-service.sh --port5000"
