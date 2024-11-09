#!/usr/bin/env python3
from pathlib import Path
import platform
import getpass
import socket
import yaml
import shutil

def get_system_info():
    username = getpass.getuser()
    hostname = socket.gethostname()
    # Clean up hostname for use in computer name
    computer_name = f"{username.title()}'s {platform.mac_ver()[0] if platform.system() == 'Darwin' else ''} Computer"
    
    return {
        "username": username,
        "computer_name": computer_name,
        "host_name": hostname.lower(),
        "local_host_name": hostname.lower(),
        "email": f"{username}@example.com"  # Default email, should be changed
    }

def setup_user_config():
    nix_dir = Path(__file__).parent.parent
    sample_path = nix_dir / "config" / "sample.user.yaml"
    user_path = nix_dir / "config" / "user.yaml"
    
    if user_path.exists():
        print(f"Configuration file already exists at {user_path}")
        return
    
    # Load sample config
    with open(sample_path) as f:
        config = yaml.safe_load(f)
    
    # Update with system info
    system_info = get_system_info()
    config.update(system_info)
    
    # Write new config
    with open(user_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"""
Configuration file created at {user_path}
Please review and adjust the following:
1. Email address
2. Computer name
3. Dock applications
4. Other preferences

You can edit the file directly or run this script again with --interactive flag.
""")

if __name__ == "__main__":
    setup_user_config() 