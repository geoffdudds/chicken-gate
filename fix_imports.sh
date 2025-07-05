#!/bin/bash
# Fix script for importlib.metadata issue

echo "🔧 Fixing importlib.metadata issue for Python 3.7..."
echo ""

# Install importlib-metadata backport for Python 3.7
echo "📦 Installing importlib-metadata backport..."
python3 -m pip install importlib-metadata

# Also install typing-extensions which might be needed
echo "📦 Installing typing-extensions..."
python3 -m pip install typing-extensions

echo ""
echo "✅ Fix complete! Try running the system again:"
echo "   python ./start_system.py"
