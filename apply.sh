#!/bin/bash
# apply.sh - Nix Configuration Update Script
# This script reapplies the nix configuration on an already set up system.

echo "This script will:"
echo "1. Pull latest changes from the repository"
echo "2. Update flake inputs"
echo "3. Build and apply new configuration"
echo "4. Verify changes were applied successfully"

# TODO: Implement the following steps:
# - Check if nix is installed
# - Pull latest changes
# - Update flake
# - Build new configuration
# - Apply changes
# - Run verification checks


#!/bin/bash
# apply.sh - System update script
set -e

[ -f ~/.dev-env-location ] && source ~/.dev-env-location

echo "🔄 Updating system configuration..."

# Update repository
cd "$DEV_ENV_PATH"
git pull

# Update flake inputs
cd nix
nix flake update

# Build and apply using core build script
"$DEV_ENV_PATH/nix/build-nix.sh"

# Verify changes
echo "✅ System updated successfully!"