#!/bin/bash
# bootstrap.sh - Full System Setup Script
# This script performs a complete setup of the development environment on a fresh macOS system.

echo "This script will:"
echo "1. Install Command Line Tools for Xcode"
echo "2. Install Nix package manager"
echo "3. Install Homebrew"
echo "4. Clone the dev-env repository"
echo "5. Set up initial configuration files"
echo "6. Apply the full nix configuration"
echo "7. Install additional tools and applications"

# TODO: Implement the following steps:
# - Check if running on macOS
# - Install Command Line Tools
# - Install Nix using determinate installer
# - Install Homebrew
# - Clone dev-env repository
# - Set up initial configuration
# - Run first nix build
# - Apply configuration
# - Set up additional tools
# - Verify installation

set -e

setup_persistent_location() {
    local location_file="$HOME/.dev-env-location"
    if [ ! -f "$location_file" ]; then
        echo "Please enter target dev-env location (default: $HOME/.dev-env):"
        read -r user_location
        DEV_ENV_PATH=${user_location:-$HOME/.dev-env}
        echo "export DEV_ENV_PATH=\"$DEV_ENV_PATH\"" > "$location_file"
    fi
    source "$location_file"
}
# Install core dependencies
install_dependencies() {
    # Install Xcode Command Line Tools if not already installed
    if ! xcode-select -p &>/dev/null; then
        echo "Installing Xcode Command Line Tools..."
        xcode-select --install || true
    else
        echo "Xcode Command Line Tools already installed"
    fi
    
    # Install Nix if not already installed
    if ! command -v nix &>/dev/null; then
        echo "Installing Nix..."
        curl -L https://nixos.org/nix/install | sh
    else
        echo "Nix already installed"
    fi
    
    # Install Homebrew if not already installed
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew already installed"
    fi
}

# Main execution
setup_persistent_location
install_dependencies

python3 "$(dirname "$0")/tools/dev_env_updater.py"

cd "$DEV_ENV_PATH/nix"
# Initial build
nix flake update
darwin-rebuild switch --flake .#default