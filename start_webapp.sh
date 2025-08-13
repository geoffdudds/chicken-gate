#!/bin/bash
# Script to start and enable the chicken gate web interface
# Use this when you upgrade to a Pi 4 or want to re-enable the web interface

echo "Starting chicken gate web interface..."

# Enable the service to auto-start
sudo systemctl enable chicken-gate-web
echo "✅ Web service enabled (will start on boot)"

# Start the service
sudo systemctl start chicken-gate-web
echo "✅ Web service started"

# Wait a moment for startup
sleep 3

# Check status
echo ""
echo "Service status:"
sudo systemctl status chicken-gate-web --no-pager -l

echo ""
echo "🎉 Web interface has been started and enabled!"
echo ""
echo "Web interface should be available at:"
echo "  http://chicken-gate (if using Tailscale MagicDNS)"
echo "  http://$(hostname -I | awk '{print $1}')"
echo "  http://localhost"
echo ""
echo "To stop and disable again:"
echo "  ./stop_webapp.sh"
