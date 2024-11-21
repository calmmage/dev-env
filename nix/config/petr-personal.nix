{ pkgs }:
{
  username = "petrlavrov";
  full_name = "Petr Lavrov";
  email = "petr.b.lavrov@gmail.com";
  computer_name = "Petr's MacBook Pro 2";
  host_name = "petrs-macbook-pro-2";
  secrets_repo_url = "git+ssh://git@github.com/calmmage/nix-secrets.git";

  homebrew = {
    brews = [
      "sonar-scanner"
    ];

    casks = [
      # Gaming & Entertainment
      "discord"
      "steam"
      "epic-games"
      "minecraft"
      
      # Creative
      "blender"
      "unity-hub"
      "obs"
      
      # Media & Communication
      "kindle"
      "whatsapp"
      "zoom"
      "vlc"
      "iina"
      
      # System & Utilities
      "aldente"
      "grandperspective"
      "lastpass"
      "flow"
    ];
  };

  packages = with pkgs; [
    # AWS & Cloud
    awscli2
    
    # Development
    cmake
    dlib
    
    # System Monitoring
    bottom
    procs
    htop
    duf
    
    # Additional Utils
    sd
    dust
    gping
    mtr
  ];
}