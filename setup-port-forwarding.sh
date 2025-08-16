#!/bin/bash

echo "🔗 Setting up port forwarding: 80 -> 5000"
echo "This allows http://chicken-gate (no port) to work with the port 5000 service"

# Enable IP forwarding
echo "📋 Enabling IP forwarding..."
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Add iptables rules to forward port 80 to 5000
echo "🔀 Adding iptables rules..."
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 5000

# Make iptables rules persistent
echo "💾 Making iptables rules persistent..."
sudo apt-get update
sudo apt-get install -y iptables-persistent

# Save current rules
sudo netfilter-persistent save

echo ""
echo "✅ Port forwarding setup complete!"
echo "🌐 You can now access:"
echo "   http://chicken-gate (forwarded to port 5000)"
echo "   http://chicken-gate:5000 (direct access)"
echo "   http://192.168.0.134 (forwarded to port 5000)"
echo "   http://192.168.0.134:5000 (direct access)"
echo ""
echo "⚙️  The chicken-gate-web service continues running on port 5000"
echo "🔒 No root privileges needed for the web app"
