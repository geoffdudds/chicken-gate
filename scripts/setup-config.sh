#!/bin/bash
# Configuration setup script for Chicken Gate

echo "🐔 Chicken Gate Configuration Setup"
echo "==================================="
echo

# Check if secret.toml already exists
if [ -f "secret.toml" ]; then
    echo "⚠️  secret.toml already exists. Backup and replace? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cp secret.toml secret.toml.backup
        echo "✅ Backed up existing secret.toml to secret.toml.backup"
    else
        echo "ℹ️  Keeping existing secret.toml"
        exit 0
    fi
fi

# Copy template
if [ -f "src/chicken_gate/shared/secret.toml.template" ]; then
    cp src/chicken_gate/shared/secret.toml.template secret.toml
    echo "✅ Created secret.toml from template"
    echo
    echo "📝 Next steps:"
    echo "1. Edit secret.toml with your actual credentials"
    echo "2. For Gmail, use an App Password (not your regular password)"
    echo "3. Alternatively, set environment variables (see docs/configuration.md)"
    echo
    echo "Environment variables (recommended for production):"
    echo "  CHICKEN_GATE_EMAIL_SENDER=your-email@gmail.com"
    echo "  CHICKEN_GATE_EMAIL_PASSWORD=your-app-password"
    echo "  CHICKEN_GATE_EMAIL_RECIPIENT=recipient@gmail.com"
else
    echo "❌ src/chicken_gate/shared/secret.toml.template not found!"
    exit 1
fi
