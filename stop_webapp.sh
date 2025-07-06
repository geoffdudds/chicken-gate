#!/bin/bash
# Script to stop and disable the chicken gate web interface
# This frees up Pi Zero resources for the gate control system

echo "Stopping chicken gate web interface..."

# Stop the service
sudo systemctl stop chicken-gate-web
echo "✅ Web service stopped"

# Disable the service from auto-starting
sudo systemctl disable chicken-gate-web
echo "✅ Web service disabled (won't start on boot)"

# Check status
echo ""
echo "Service status:"
sudo systemctl status chicken-gate-web --no-pager -l

echo ""
echo "🎉 Web interface has been stopped and disabled!"
echo ""
echo "The gate control system now has full Pi Zero resources."
echo "Gate timers and positioning should work much better now."
echo ""
echo "To re-enable when you get a Pi 4:"
echo "  sudo systemctl enable chicken-gate-web"
echo "  sudo systemctl start chicken-gate-web"
echo ""
echo "Or run: ./start_webapp.sh"
