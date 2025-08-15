#!/bin/bash

echo "� Installing/Updating Chicken Gate Main Service"
echo "==============================================="

echo "📋 Installing service file (chicken-gate.service)..."
sudo cp ./systemd/chicken-gate.service /etc/systemd/system/

echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Kill any manually running gate processes
echo "🧹 Cleaning up manual processes..."
pkill -f "chicken-gate-main" 2>/dev/null || true
pkill -f "chicken_gate.gate.main" 2>/dev/null || true
pkill -f "src/main.py" 2>/dev/null || true  # Old direct invocation
sleep 2  # Give processes time to terminate

echo "🚀 Enabling and starting chicken-gate service..."
sudo systemctl enable chicken-gate.service
sudo systemctl restart chicken-gate.service

# Show status
echo ""
echo "📊 Service Status:"
sudo systemctl status chicken-gate.service --no-pager

echo ""
echo "✅ Installation complete!"

echo ""
echo "📋 Service manages:"
echo "   🏠 Gate hardware control (GPIO pins)"
echo "   📊 Status file writing (gate_status.json)"
echo "   📝 Command file monitoring (gate_cmd.txt)"
echo "   ⏰ Scheduled operations"

echo ""
echo "📁 Related files:"
echo "   Service: /etc/systemd/system/chicken-gate.service"
echo "   Status: ~/sw/chicken-gate/gate_status.json"
echo "   Commands: ~/sw/chicken-gate/gate_cmd.txt"

echo ""
echo "🔍 To check logs:"
echo "   sudo journalctl -u chicken-gate -f"
echo "   sudo journalctl -u chicken-gate -n 50"

echo ""
echo "🌐 Note: Web interface depends on this service"
echo "   If this service fails, the web interface won't work properly"