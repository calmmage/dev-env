{
  username = "petr";
  email = "petr@superlinear.com";
  computer_name = "Petr's MacBook Pro";
  host_name = "petrs-macbook-pro";

  default_browser = "chrome";

  dock = {
    settings = {
      # Visual settings
      autohide = true;
      magnification = true;
      tile_size = 36;
      large_size = 128;
      position = "bottom";  # Can be "bottom", "left", or "right"
      mru_spaces = false; # disable reordering spaces automatically based on recent usage (I hate them chaotically reordering)

      # Behavior settings
      expose_group_by_app = true;
      minimize_to_application = true;
      show_recent_apps = true;
      show_process_indicators = true;
    };

    apps = [
      "/Applications/Raycast.app"
      "/System/Applications/System Settings.app"
    ];
  };

  homebrew = {
    brews = [
      # Development essentials that work better with brew
      # "poetry"
      # "ripgrep"
      "python@3.11"
      "python@3.12"
      "node" # Node.js - often better to use brew for JS ecosystem
      "git-lfs" # Git Large File Storage
      "gcc" # GNU Compiler Collection
      "sonar-scanner"
      "yarn" # Adding yarn package manager
      # add fkill? how?
    ];

    casks = [

        # Development
        "docker"  # docker desktop app
        "jetbrains-toolbox"
        "pycharm"
        # - sourcetree
        "github" # github desktop app
        "launchcontrol"
        "warp"
        # - mitmproxy
        "cursor"
        # "zed"
        "karabiner-elements"
        "sublime-text"

        # Browsers & Communication
        "google-chrome"
        "slack"
        "telegram"

        # Productivity & Utils
        "raycast"
        "rectangle" # window manager
        # "dropbox"
        "obsidian"
        "notion"
        "chatgpt"
        # - shottr # Alternative: CleanShot X - installed through setapp
        # - bartender # through setapp

        # App marketplace
        "setapp"
        # todo: add instructions for user to install apps manually
        # paste
        # cleanshotX
        # bartender
        # popclip
        # hazeover

        # Creative
        "adobe-creative-cloud"

        # Suggestions from Claude

        # Media Processing & Conversion
        # "ffmpeg"          # Swiss army knife for audio/video processing
        # "imagemagick"     # Powerful image manipulation tool
        # "handbrake"       # Video transcoder
        # "yt-dlp"          # Download videos from YouTube and other sites

        # # Development Tools
        # "neovim"          # Modern, extensible text editor
        # "tmux"            # Terminal multiplexer for multiple sessions
        # "httpie"          # User-friendly HTTP client
        # "mkcert"          # Make locally-trusted development certificates

        # # System Monitoring & Performance
        # "glances"         # System monitoring tool

        # # Network Tools
        # "nmap"            # Network exploration and security scanning
        # "wireshark"       # Network protocol analyzer
        # "netcat"         # Networking utility for reading/writing network connections
        # "mtr"             # Network diagnostic tool

        # # Security & Encryption
        # "gnupg"           # GNU Privacy Guard encryption
        # "bitwarden"       # Password manager
        # "1password"      # Popular password manager alternative
        # "veracrypt"       # Disk encryption software

        # # Productivity
        # "taskwarrior"     # Command-line task management
        # "pandoc"          # Universal document converter
        # "asciinema"       # Terminal session recorder

        # # Database Tools
        # - pgcli           # PostgreSQL CLI with auto-completion
        # - mycli           # MySQL/MariaDB CLI with auto-completion
        # "dbeaver"         # Universal database tool
        # "mongodb-compass" # MongoDB GUI

        # # Cloud & Infrastructure
        # - terraform       # Infrastructure as code
        # - kubernetes-cli  # Kubernetes command-line tool
        # "helm"            # Kubernetes package manager
        # "vagrant"         # Development environment creation

        # # File Management
        # "ranger"          # Console file manager with VI keybindings
        # "fzf"             # Command-line fuzzy finder
        # "rsync"           # Fast file copying tool

        # Personal & Entertainment
        # "discord"           # Gaming chat and communities
        # "steam"            # Gaming platform
        # "epic-games"       # Epic Games store
        # "obs"              # Streaming and recording
        # "kindle"           # Amazon's e-book reader
        # "whatsapp"         # Messaging app
        # "zoom"             # Video conferencing

        # Gaming & Creative
        # "blender"          # 3D creation suite
        # "unity-hub"        # Game development platform
        # "minecraft"        # Gaming

        # System & Utilities
        "aldente"          # Battery management
        # "amphetamine"      # Keep system awake # missing in brew
        "grandperspective" # Disk space visualization
        # "hand-mirror"      # Quick camera check # via setapp
        # "hp-smart"         # Printer utilities
        "lastpass"         # Password manager
        # "dropover"         # Drag and drop enhancement # missing in brew - install via setapp

        # Media & Entertainment
        "vlc"              # Media player
        "iina"            # Modern media player for macOS
        # install via app store
        # "flow"
    ];
  };

}