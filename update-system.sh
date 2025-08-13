#!/bin/bash
# Update script for Raspberry Pi to get newer gpiozero

echo "🔄 Updating Raspberry Pi system and gpiozero..."
echo "This will update your system packages and Python libraries."
echo ""

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Upgrade system packages
echo "⬆️ Upgrading system packages..."
sudo apt upgrade -y

# Update pip to latest version
echo "🐍 Updating pip..."
python3 -m pip install --upgrade pip

# Update gpiozero to latest version
echo "📡 Updating gpiozero..."
python3 -m pip install --upgrade gpiozero

# Check versions
echo ""
echo "✅ Update complete! Current versions:"
echo "Python version: $(python3 --version)"
echo "pip version: $(python3 -m pip --version)"
echo "gpiozero version: $(python3 -c 'import gpiozero; print(gpiozero.__version__)')"

echo ""
echo "🎉 System update finished!"
echo "You can now use newer gpiozero features like 'active_low' parameter."
