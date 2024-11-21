{ pkgs }:
let
  shared = import ./shared.nix { inherit pkgs; };
in
{
  username = "petrlavrov";
  full_name = "Petr Lavrov";
  email = "petr.b.lavrov@gmail.com";
  computer_name = "Petr's MacBook Pro 2";
  host_name = "petrs-macbook-pro-2";
  secrets_repo_url = "git+ssh://git@github.com/calmmage/nix-secrets.git";

  homebrew = {
    brews = shared.homebrew.brews ++ [
      # "sonar-scanner" is commented out
    ];

    casks = shared.homebrew.casks ++ [
        # Personal & Entertainment
        "discord"           # Gaming chat and communities
        "steam"            # Gaming platform
        "epic-games"       # Epic Games store
        "obs"              # Streaming and recording
        "kindle"           # Amazon's e-book reader
        "whatsapp"         # Messaging app
        "zoom"             # Video conferencing

        # Gaming & Creative
        "blender"          # 3D creation suite
        "unity-hub"        # Game development platform
        "minecraft"        # Gaming
        # "adobe-creative-cloud"

        # System & Utilities
        "grandperspective" # Disk space visualization
        "lastpass"         # Password manager

        # installing via setapp
        # "dropover"         # Drag and drop enhancement 
        # "hand-mirror"      # Quick camera check
        # "aldente"          # Battery management

        # Media & Entertainment
        "vlc"              # Media player
        "iina"            # Modern media player for macOS
    ];

    masApps = shared.homebrew.masApps // {
      "hp-smart" = 1474276998;
      "amphetamine" = 937984704;
    };
  };

  packages = shared.packages ++ (with pkgs; [
    # Add personal-specific packages here
  ]);
}