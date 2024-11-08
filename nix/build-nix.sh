#!/bin/bash

# Exit on error
set -e

echo "🚀 Building and applying Nix configuration..."

# Check if nix daemon is running
if ! pgrep nix-daemon > /dev/null; then
    echo "⚠️  Nix daemon is not running. Attempting to start it..."
    sudo launchctl load /Library/LaunchDaemons/org.nixos.nix-daemon.plist
    
    # Wait a moment for the daemon to start
    sleep 2
fi

echo "🔄 Rebuilding darwin-rebuild..."
darwin-rebuild switch --flake .#default

echo "✅ Nix configuration applied successfully!" 