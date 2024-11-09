#!/bin/bash
# build-nix.sh - Core nix build script with update options
set -e

# Source dev-env location
[ -f ~/.dev-env-location ] && source ~/.dev-env-location

if [ -z "$DEV_ENV_PATH" ]; then
    echo "Error: DEV_ENV_PATH is not set. Please run bootstrap.sh first."
    exit 1
fi

# Parse arguments
UPDATE_GIT=false
UPDATE_FLAKE=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --update|--up|-u) UPDATE_GIT=true; UPDATE_FLAKE=true ;;
        --flake|-f) UPDATE_FLAKE=true ;;
        --git|-g) UPDATE_GIT=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

cd "$DEV_ENV_PATH/nix"

# Optional git update
if [ "$UPDATE_GIT" = true ]; then
    echo "🔄 Updating repository..."
    git pull
fi

# Optional flake update
if [ "$UPDATE_FLAKE" = true ]; then
    echo "🔄 Updating flake inputs..."
    nix flake update
fi

# Ensure nix daemon is running
if ! pgrep nix-daemon > /dev/null; then
    echo "⚠️  Starting nix daemon..."
    sudo launchctl load /Library/LaunchDaemons/org.nixos.nix-daemon.plist
    sleep 2
fi

# Build and apply
echo "🔄 Building configuration..."
darwin-rebuild switch --flake .#default